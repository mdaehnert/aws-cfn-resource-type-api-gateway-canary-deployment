from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient

from .models import ResourceModel

CREATED = "CREATED"


def handle_update(agw_client: APIGatewayClient, model: ResourceModel,
                  callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )

    if callback_context.get("green-status") == CREATED:
        stage_name = "blue"
        final_state = OperationStatus.SUCCESS
        # first new deploymentId in canaries with given percentage.
        # Then wait for 15 Minutes
        # then deploy new deployment id
        # then remove canary
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
                    "value": model.TracingEnabled
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
                    "value": model.TracingEnabled
                }
            ]
        )
    callback_context[f"{stage_name}-status"] = CREATED
    progress.callbackContext = callback_context
    progress.status = final_state
    return progress
