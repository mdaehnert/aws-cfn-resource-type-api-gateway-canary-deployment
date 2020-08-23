from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent
from mypy_boto3_apigateway import APIGatewayClient

from .models import ResourceModel

DELETED = "DELETED"


def handle_delete(agw_client: APIGatewayClient, model: ResourceModel,
                  callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    if callback_context.get("blue-status") is None:
        agw_client.delete_stage(
            restApiId=model.RestApiId,
            stageName="blue"
        )
        callback_context["blue-status"] = DELETED
        return ProgressEvent(
            status=OperationStatus.IN_PROGRESS,
            resourceModel=model,
            callbackContext=callback_context,
        )
    else:
        agw_client.delete_stage(
            restApiId=model.RestApiId,
            stageName="green"
        )
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
        )
