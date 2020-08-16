from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient

from .models import ResourceModel

DELETED = "DELETED"


def handle_delete(agw_client: APIGatewayClient, model: ResourceModel,
                  callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    progress = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )

    if callback_context.get("blue-status") == DELETED:
        stage_name = "green"
        final_state = OperationStatus.SUCCESS
    else:
        stage_name = "blue"
        final_state = OperationStatus.IN_PROGRESS

    agw_client.delete_stage(
        restApiId=model.RestApiId,
        stageName=stage_name
    )
    callback_context[f"{stage_name}-status"] = DELETED
    progress.callbackContext = callback_context
    progress.status = final_state
    return progress
