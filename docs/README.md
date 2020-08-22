# SPRT::ApiGateway::Deployment

Deploys a REST API to ablue and a green stage with canary settings and deployment hooks for tests against the green stage.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "SPRT::ApiGateway::Deployment",
    "Properties" : {
        "<a href="#deploymentid" title="DeploymentId">DeploymentId</a>" : <i>String</i>,
        "<a href="#restapiid" title="RestApiId">RestApiId</a>" : <i>String</i>,
        "<a href="#tracingenabled" title="TracingEnabled">TracingEnabled</a>" : <i>Boolean</i>,
        "<a href="#canarypercentage" title="CanaryPercentage">CanaryPercentage</a>" : <i>String</i>,
        "<a href="#greenteststatemachinearn" title="GreenTestStateMachineArn">GreenTestStateMachineArn</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: SPRT::ApiGateway::Deployment
Properties:
    <a href="#deploymentid" title="DeploymentId">DeploymentId</a>: <i>String</i>
    <a href="#restapiid" title="RestApiId">RestApiId</a>: <i>String</i>
    <a href="#tracingenabled" title="TracingEnabled">TracingEnabled</a>: <i>Boolean</i>
    <a href="#canarypercentage" title="CanaryPercentage">CanaryPercentage</a>: <i>String</i>
    <a href="#greenteststatemachinearn" title="GreenTestStateMachineArn">GreenTestStateMachineArn</a>: <i>String</i>
</pre>

## Properties

#### DeploymentId

The ID of an API Gateway deployment that should be released to a blue and a green stage.

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### RestApiId

Identifies the API Gateway REST API that should be deployed to a blue and a green stage.

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### TracingEnabled

Enables X-Ray tracing for both API Gateway stages.

_Required_: No

_Type_: Boolean

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### CanaryPercentage

Percentage of the traffic that is routed to an updated deployment for 15 minutes. Provide this value to enable canary deployments and configure CloudWatch alarms and CloudFormation rollback triggers to roll back when canaries do not work as expected.

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### GreenTestStateMachineArn

ARN of an AWS StepFunction that executes automatich tests against the green stage of the API Gateway after deployment. This STepFunction has to succeed, before the canary deployment on the blue stage starts.

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the StageName.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### StageName

The name of the blue stage.

