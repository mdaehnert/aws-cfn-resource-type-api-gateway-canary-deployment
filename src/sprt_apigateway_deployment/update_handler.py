from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient

from .models import ResourceModel

CREATED = "CREATED"


def handle_update(agw_client: APIGatewayClient, model: ResourceModel, previous_state: ResourceModel,
                  callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )

    if callback_context.get("green-status") == CREATED:
        stage_name = "blue"
        final_state = OperationStatus.SUCCESS
        if model.DeploymentId != previous_state.DeploymentId:
            if model.CanaryPercentage is not None:
                if callback_context.get("canary-counter") is None:
                    agw_client.update_stage(
                        restApiId=model.RestApiId,
                        stageName=stage_name,
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
                    callback_context["canary-counter"] = 0
                    progress.callbackContext = callback_context
                    progress.status = OperationStatus.IN_PROGRESS
                    progress.callbackDelaySeconds = 60
                    return progress
                elif callback_context.get("canary-counter") < 15:
                    callback_context["canary-counter"] = callback_context["canary-counter"] + 1
                    progress.callbackContext = callback_context
                    progress.status = OperationStatus.IN_PROGRESS
                    progress.callbackDelaySeconds = 60
                    return progress
                else:
                    agw_client.update_stage(
                        restApiId=model.RestApiId,
                        stageName=stage_name,
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
                    progress.callbackContext = callback_context
                    progress.status = OperationStatus.SUCCESS
                    return progress
            else:
                agw_client.update_stage(
                    restApiId=model.RestApiId,
                    stageName=stage_name,
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
        else:
            agw_client.update_stage(
                restApiId=model.RestApiId,
                stageName=stage_name,
                patchOperations=[
                    {
                        "op": "replace",
                        "path": "/tracingEnabled",
                        "value": str(model.TracingEnabled)
                    }
                ]
            )
    else:
        stage_name = "green"
        final_state = OperationStatus.IN_PROGRESS
        agw_client.update_stage(
            restApiId=model.RestApiId,
            stageName=stage_name,
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
    callback_context[f"{stage_name}-status"] = CREATED
    progress.callbackContext = callback_context
    progress.status = final_state
    return progress
