# SPRT::ApiGateway::Deployment

Deploys REST APIs with canary settings.

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
        "<a href="#canarypercentage" title="CanaryPercentage">CanaryPercentage</a>" : <i>String</i>
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
</pre>

## Properties

#### DeploymentId

A TPS Code is automatically generated on creation and assigned as the unique identifier.

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### RestApiId

A TPS Code is automatically generated on creation and assigned as the unique identifier.

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### TracingEnabled

A TPS Code is automatically generated on creation and assigned as the unique identifier.

_Required_: No

_Type_: Boolean

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### CanaryPercentage

The title of the TPS report is a mandatory element.

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

A TPS Code is automatically generated on creation and assigned as the unique identifier.

