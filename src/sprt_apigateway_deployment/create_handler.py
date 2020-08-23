from typing import MutableMapping, Any

from cloudformation_cli_python_lib import OperationStatus, ProgressEvent, HandlerErrorCode
from mypy_boto3_apigateway.client import APIGatewayClient

from .models import ResourceModel

CREATED = "CREATED"


def handle_create(agw_client: APIGatewayClient, model: ResourceModel,
                  callback_context: MutableMapping[str, Any]) -> ProgressEvent:
    if callback_context.get("green-status") == CREATED:
        stage_name = "blue"
        final_state = OperationStatus.SUCCESS
    else:
        stage_name = "green"
        final_state = OperationStatus.IN_PROGRESS
    try:
        agw_client.create_stage(
            restApiId=model.RestApiId,
            stageName=stage_name,
            deploymentId=model.DeploymentId,
            description=f"{stage_name} production stage",
            cacheClusterEnabled=False,
            tracingEnabled=model.TracingEnabled
        )
    except agw_client.exceptions.NotFoundException:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NotFound,
            message="REST API does not exist"
        )
    model.StageName = "blue"
    callback_context[f"{stage_name}-status"] = CREATED
    return ProgressEvent(
        status=final_state,
        callbackContext=callback_context,
        resourceModel=model,
    )
