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
    progress = ProgressEvent(status=OperationStatus.IN_PROGRESS)

    if callback_context.get("green-status") is None:
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
        progress.callbackDelaySeconds = 30
        progress.status = OperationStatus.IN_PROGRESS
    elif callback_context.get("green-status") == READY_FOR_TESTING:
        LOG.debug("initiating green tests")
        callback_context["green-status"] = TESTING
        execution_arn = states_client.start_execution(stateMachineArn=model.GreenTestStateMachineArn)["executionArn"]
        callback_context["green-test-execution-arn"] = execution_arn
        progress.callbackDelaySeconds = 2
        progress.status = OperationStatus.IN_PROGRESS
    elif callback_context.get("green-status") == TESTING:
        test_status = states_client.describe_execution(
            executionArn=callback_context["green-test-execution-arn"]
        )["status"]
        if test_status == "RUNNING":
            LOG.debug("Tests still running")
            progress.status = OperationStatus.IN_PROGRESS
            progress.callbackDelaySeconds = 2
        elif test_status == "SUCCEEDED":
            LOG.debug("Tests succeeded")
            progress.status = OperationStatus.IN_PROGRESS
            callback_context["green-status"] = DONE
        else:
            LOG.debug("Tests failed")
            progress.status = OperationStatus.FAILED
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
                    progress.status = OperationStatus.IN_PROGRESS
                    progress.callbackDelaySeconds = 900
                else:
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
                    progress.status = OperationStatus.SUCCESS
            else:
                agw_client.update_stage(
                    restApiId=model.RestApiId,
                    stageName="blue",
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
                progress.status = OperationStatus.SUCCESS
        else:
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
                        "path": "/tracingEnabled",
                        "value": str(model.TracingEnabled)
                    }
                ]
            )
            progress.status = OperationStatus.SUCCESS

    progress.resourceModel = model
    progress.callbackContext = callback_context
    return progress
