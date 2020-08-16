import logging
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from .create_handler import handle_create
from .delete_handler import handle_delete
from .models import ResourceHandlerRequest, ResourceModel

from .update_handler import handle_update

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(10)
TYPE_NAME = "SPRT::ApiGateway::Deployment"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    LOG.debug(callback_context)
    LOG.debug(request.desiredResourceState)
    try:
        if isinstance(session, SessionProxy):
            client = session.client("apigateway")

            progress = handle_create(
                agw_client=client,
                model=model,
                callback_context=callback_context
            )
            return progress
        else:
            LOG.error("No session available")
            raise TypeError
    except TypeError as e:
        raise exceptions.InternalFailure(f"was not expecting type {e}")


@resource.handler(Action.UPDATE)
def update_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    LOG.debug(callback_context)
    LOG.debug(request.previousResourceState)
    LOG.debug(request.desiredResourceState)
    try:
        if isinstance(session, SessionProxy):
            client = session.client("apigateway")

            progress = handle_update(
                agw_client=client,
                model=model,
                callback_context=callback_context
            )
            return progress
        else:
            LOG.error("No session available")
            raise TypeError
    except TypeError as e:
        raise exceptions.InternalFailure(f"was not expecting type {e}")


@resource.handler(Action.DELETE)
def delete_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    LOG.debug(callback_context)
    try:
        if isinstance(session, SessionProxy):
            client = session.client("apigateway")

            progress = handle_delete(
                agw_client=client,
                model=model,
                callback_context=callback_context
            )
            return progress
        else:
            LOG.error("No session available")
            raise TypeError
    except TypeError as e:
        raise exceptions.InternalFailure(f"was not expecting type {e}")


@resource.handler(Action.READ)
def read_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    LOG.debug(callback_context)

    # TODO: put code here
    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )


@resource.handler(Action.LIST)
def list_handler(
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    LOG.debug(callback_context)

    # TODO: put code here
    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModels=[],
    )
