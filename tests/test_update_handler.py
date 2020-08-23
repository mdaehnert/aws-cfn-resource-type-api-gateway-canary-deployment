import unittest
from unittest.mock import Mock

from cloudformation_cli_python_lib import OperationStatus

import src.sprt_apigateway_deployment.update_handler as uut
from src.sprt_apigateway_deployment.models import ResourceModel


class TestUpdateHandler(unittest.TestCase):

    def test_deploy_green(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={}
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.READY_FOR_TESTING)
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)
        agw_client.update_stage.assert_called_once()

    def test_deploy_green_without_tests(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment_without_tests,
            previous_state=previous_state,
            callback_context={}
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.DONE)
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)
        agw_client.update_stage.assert_called_once()

    def test_deploy_green_without_new_agw_deployment(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=previous_state,
            previous_state=previous_state,
            callback_context={}
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.DONE)
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)
        agw_client.update_stage.assert_called_once()

    def test_start_green_tests(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        states_client = Mock()
        states_client.start_execution = Mock(return_value={"executionArn": "testExecution"})

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={uut.GREEN_STATUS: uut.READY_FOR_TESTING}
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.TESTING)
        self.assertEqual(progress_event.callbackContext[uut.GREEN_TEST_EXECUTION_ARN], "testExecution")
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)

    def test_green_tests_in_progress(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        states_client = Mock()
        states_client.describe_execution = Mock(return_value={"status": "RUNNING"})

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.TESTING,
                uut.GREEN_TEST_EXECUTION_ARN: "testExecution"
            }
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.TESTING)
        self.assertEqual(progress_event.callbackContext[uut.GREEN_TEST_EXECUTION_ARN], "testExecution")
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)

    def test_green_tests_succeeded(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        states_client = Mock()
        states_client.describe_execution = Mock(return_value={"status": "SUCCEEDED"})

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.TESTING,
                uut.GREEN_TEST_EXECUTION_ARN: "testExecution"
            }
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.GREEN_STATUS], uut.DONE)
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)

    def test_green_tests_failed(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        states_client = Mock()
        states_client.describe_execution = Mock(return_value={"status": "FAILED"})

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.TESTING,
                uut.GREEN_TEST_EXECUTION_ARN: "testExecution"
            }
        )

        # Then
        self.assertEqual(progress_event.status, OperationStatus.FAILED)

    def test_deploy_canaries(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.DONE
            }
        )

        # Then
        self.assertEqual(progress_event.callbackContext[uut.BLUE_STATUS], uut.CANARY)
        self.assertEqual(progress_event.status, OperationStatus.IN_PROGRESS)
        self.assertEqual(progress_event.callbackDelaySeconds, 900)
        agw_client.update_stage.assert_called_once()

    def test_promote_canaries(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.DONE,
                uut.BLUE_STATUS: uut.CANARY
            }
        )

        # Then
        self.assertEqual(progress_event.status, OperationStatus.SUCCESS)
        agw_client.update_stage.assert_called_once()

    def test_deploy_without_canaries(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=new_deployment_without_canaries,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.DONE
            }
        )

        # Then
        self.assertEqual(progress_event.status, OperationStatus.SUCCESS)
        agw_client.update_stage.assert_called_once()

    def test_deploy_without_new_api_gateway_deployment(self):
        # Given
        agw_client = Mock()
        agw_client.get_stage = Mock(return_value={"deploymentId": "oldDeployment"})
        agw_client.update_stage = Mock()
        states_client = Mock()

        # When
        progress_event = uut.handle_update(
            agw_client=agw_client,
            states_client=states_client,
            model=previous_state,
            previous_state=previous_state,
            callback_context={
                uut.GREEN_STATUS: uut.DONE
            }
        )

        # Then
        self.assertEqual(progress_event.status, OperationStatus.SUCCESS)
        agw_client.update_stage.assert_called_once()


previous_state = ResourceModel(
    DeploymentId="oldDeployment",
    RestApiId="testRestId",
    TracingEnabled=True,
    StageName="blue",
    GreenTestStateMachineArn="arn:aws:...",
    CanaryPercentage=15
)

new_deployment = ResourceModel(
    DeploymentId="newDeployment",
    RestApiId="testRestId",
    TracingEnabled=True,
    StageName="blue",
    GreenTestStateMachineArn="arn:aws:...",
    CanaryPercentage=15
)

new_deployment_without_canaries = ResourceModel(
    DeploymentId="newDeployment",
    RestApiId="testRestId",
    TracingEnabled=True,
    StageName="blue",
    GreenTestStateMachineArn="arn:aws:...",
    CanaryPercentage=None
)

new_deployment_without_tests = ResourceModel(
    DeploymentId="newDeployment",
    RestApiId="testRestId",
    TracingEnabled=True,
    StageName="blue",
    GreenTestStateMachineArn=None,
    CanaryPercentage=15
)
