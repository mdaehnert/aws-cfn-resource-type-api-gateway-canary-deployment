import logging
from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient
from mypy_boto3_stepfunctions import SFNClient

from .models import ResourceModel

CANARY = "CANARY"

READY_FOR_TESTING = "READY_FOR_TESTING"
TESTING = "TESTING"
DONE = "DONE"

LOG = logging.getLogger(__name__)
LOG.setLevel(10)


def handle_update(agw_client: APIGatewayClient, states_client: SFNClient, model: ResourceModel,
                  previous_state: ResourceModel, callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    if callback_context.get("green-status") is None:
        progress = _deploy_to_green_stage(agw_client, callback_context, model)
    elif callback_context.get("green-status") == READY_FOR_TESTING:
        progress = _start_green_tests(callback_context, model, states_client)
    elif callback_context.get("green-status") == TESTING:
        progress = _check_test_status(callback_context, states_client)
    else:
        actual_deployment_id = previous_state.DeploymentId
        if model.DeploymentId != previous_state.DeploymentId:
            actual_deployment_id = agw_client.get_stage(
                restApiId=model.RestApiId,
                stageName="blue"
            )["deploymentId"]
        if model.DeploymentId != actual_deployment_id:
            if model.CanaryPercentage is not None:
                if callback_context.get("blue-status") is None:
                    progress = _deploy_canaries(agw_client, callback_context, model)
                else:
                    progress = _promote_canaries(agw_client, model)
            else:
                progress = _deploy_to_blue_stage(agw_client, model)
        else:
            progress = _deploy_to_blue_stage(agw_client, model)

    progress.resourceModel = model
    progress.callbackContext = callback_context
    return progress


def _deploy_to_blue_stage(agw_client, model):
    agw_client.update_stage(
        restApiId=model.RestApiId,
        stageName="blue",
        patchOperations=[
            {
                "op": "remove",
                "path": "/canarySettings"
            },
            {
                "op": "replace",
                "path": "/deploymentId",
                "value": model.DeploymentId
            },
            {
                "op": "replace",
                "path": "/tracingEnabled",
                "value": str(model.TracingEnabled)
            }
        ]
    )
    return ProgressEvent(status=OperationStatus.SUCCESS)


def _promote_canaries(agw_client, model):
    agw_client.update_stage(
        restApiId=model.RestApiId,
        stageName="blue",
        patchOperations=[
            {
                "op": "remove",
                "path": "/canarySettings"
            },
            {
                "op": "replace",
                "path": "/deploymentId",
                "value": model.DeploymentId
            }
        ]
    )
    return ProgressEvent(status=OperationStatus.SUCCESS)


def _deploy_canaries(agw_client, callback_context, model):
    agw_client.update_stage(
        restApiId=model.RestApiId,
        stageName="blue",
        patchOperations=[
            {
                "op": "replace",
                "path": "/canarySettings/percentTraffic",
                "value": model.CanaryPercentage
            },
            {
                "op": "replace",
                "path": "/canarySettings/deploymentId",
                "value": model.DeploymentId
            },
            {
                "op": "replace",
                "path": "/tracingEnabled",
                "value": str(model.TracingEnabled)
            }
        ]
    )
    callback_context["blue-status"] = CANARY
    return ProgressEvent(status=OperationStatus.IN_PROGRESS, callbackDelaySeconds=900)


def _check_test_status(callback_context, states_client):
    test_status = states_client.describe_execution(
        executionArn=callback_context["green-test-execution-arn"]
    )["status"]
    if test_status == "RUNNING":
        LOG.debug("Tests still running")
        return ProgressEvent(status=OperationStatus.IN_PROGRESS, callbackDelaySeconds=2)
    elif test_status == "SUCCEEDED":
        LOG.debug("Tests succeeded")
        callback_context["green-status"] = DONE
        return ProgressEvent(status=OperationStatus.IN_PROGRESS)
    else:
        LOG.debug("Tests failed")
        return ProgressEvent(status=OperationStatus.FAILED)


def _start_green_tests(callback_context, model, states_client):
    LOG.debug("initiating green tests")
    callback_context["green-status"] = TESTING
    execution_arn = states_client.start_execution(stateMachineArn=model.GreenTestStateMachineArn)["executionArn"]
    callback_context["green-test-execution-arn"] = execution_arn
    return ProgressEvent(status=OperationStatus.IN_PROGRESS, callbackDelaySeconds=2)


def _deploy_to_green_stage(agw_client, callback_context, model):
    LOG.debug("entering green update")
    if model.GreenTestStateMachineArn is None:
        LOG.debug("No tests for green stage")
        callback_context["green-status"] = DONE
    else:
        LOG.debug("Preparing green tests")
        callback_context["green-status"] = READY_FOR_TESTING
    agw_client.update_stage(
        restApiId=model.RestApiId,
        stageName="green",
        patchOperations=[
            {
                "op": "replace",
                "path": "/deploymentId",
                "value": model.DeploymentId
            },
            {
                "op": "replace",
                "path": "/tracingEnabled",
                "value": str(model.TracingEnabled)
            }
        ]
    )
    return ProgressEvent(status=OperationStatus.IN_PROGRESS, callbackDelaySeconds=30)
