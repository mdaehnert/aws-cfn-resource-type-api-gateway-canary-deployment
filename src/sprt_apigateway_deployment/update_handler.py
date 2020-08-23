import logging
from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient
from mypy_boto3_stepfunctions import SFNClient

from .models import ResourceModel

# State Keys in CallbackContext
GREEN_TEST_EXECUTION_ARN = "GreenTestExecutionArn"
GREEN_STATUS = "GreenStatus"
BLUE_STATUS = "BlueStatus"

# States
READY_FOR_TESTING = "READY_FOR_TESTING"
TESTING = "TESTING"
DONE = "DONE"
CANARY = "CANARY"

LOG = logging.getLogger(__name__)
LOG.setLevel(10)


def handle_update(agw_client: APIGatewayClient, states_client: SFNClient, model: ResourceModel,
                  previous_state: ResourceModel, callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    actual_deployment_id = previous_state.DeploymentId
    if model.DeploymentId != previous_state.DeploymentId:
        actual_deployment_id = agw_client.get_stage(
            restApiId=model.RestApiId,
            stageName="blue"
        )["deploymentId"]
    if callback_context.get(GREEN_STATUS) is None:
        return _deploy_to_green_stage(agw_client, callback_context, model, actual_deployment_id)
    elif callback_context.get(GREEN_STATUS) == READY_FOR_TESTING:
        return _start_green_tests(callback_context, model, states_client)
    elif callback_context.get(GREEN_STATUS) == TESTING:
        return _check_test_status(callback_context, states_client, model)
    else:
        if model.DeploymentId != actual_deployment_id and model.CanaryPercentage is not None:
            if callback_context.get(BLUE_STATUS) is None:
                return _deploy_canaries(agw_client, callback_context, model)
            else:
                return _promote_canaries(agw_client, model)
        else:
            return _deploy_to_blue_stage(agw_client, model)


def _deploy_to_green_stage(agw_client, callback_context, model, actual_deployment_id):
    LOG.debug("entering green update")
    if model.GreenTestStateMachineArn is None or model.DeploymentId == actual_deployment_id:
        LOG.debug("No tests for green stage")
        callback_context[GREEN_STATUS] = DONE
    else:
        LOG.debug("Preparing green tests")
        callback_context[GREEN_STATUS] = READY_FOR_TESTING
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
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        callbackDelaySeconds=30,
        resourceModel=model,
        callbackContext=callback_context
    )


def _start_green_tests(callback_context, model, states_client):
    LOG.debug("initiating green tests")
    callback_context[GREEN_STATUS] = TESTING
    execution_arn = states_client.start_execution(stateMachineArn=model.GreenTestStateMachineArn)["executionArn"]
    callback_context[GREEN_TEST_EXECUTION_ARN] = execution_arn
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        callbackDelaySeconds=2,
        resourceModel=model,
        callbackContext=callback_context
    )


def _check_test_status(callback_context, states_client, model):
    test_status = states_client.describe_execution(
        executionArn=callback_context[GREEN_TEST_EXECUTION_ARN]
    )["status"]
    if test_status == "RUNNING":
        LOG.debug("Tests still running")
        return ProgressEvent(
            status=OperationStatus.IN_PROGRESS,
            callbackDelaySeconds=2,
            resourceModel=model,
            callbackContext=callback_context
        )
    elif test_status == "SUCCEEDED":
        LOG.debug("Tests succeeded")
        callback_context[GREEN_STATUS] = DONE
        return ProgressEvent(status=OperationStatus.IN_PROGRESS, resourceModel=model, callbackContext=callback_context)
    else:
        LOG.debug("Tests failed")
        return ProgressEvent(status=OperationStatus.FAILED, resourceModel=model)


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
    callback_context[BLUE_STATUS] = CANARY
    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        callbackDelaySeconds=900,
        resourceModel=model,
        callbackContext=callback_context
    )


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
    return ProgressEvent(status=OperationStatus.SUCCESS, resourceModel=model)


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
    return ProgressEvent(status=OperationStatus.SUCCESS, resourceModel=model)
