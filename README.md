# SPRT::ApiGateway::Deployment

This resource type enables blue/green deployments with canaries and automatic tests via CloudFormation. The resource
provider will generate two stages in given REST API of the API Gateway called _blue_ and _green_. If you create a
deployment in the same template this deployment will be released to both stages.  
Upon update, you can execute a given AWS StepFunction that runs tests against the green stage of your API and you can
configure canary percentages. Canaries will receive traffic for 15 minutes on the blue stage. After that, the change
will be promoted completely. Use CloudWatch alarms and CloudFormation rollback triggers to handle errors on Canaries. 


## How to use
Deploy this resource with `cfn submit`


## Example
`example/infrastructure.yaml` is a template that demonstrates how to use this resource. It contains a simple
"Hello World" That is invoked via API Gateway. A test lambda verifies this at the API with a simple http request. If 
you want to deploy changes, change the logical ID of the lambda function version and the deployment to force a
replacement. This should usually be automated, like SAM does it for Lambda versions or via CDK.


## Unit Tests
Additional unit tests are located in `tests` and can be executed with `pytest`


## FAQ
_Q: Why does this resource deploy two stages at once?_  
A: Leveraging the default stage resource with a blue/green implementation of the API-Gateway deployment resource type
would make it easier to create one CloudFormation resource per API resource. However, the default stage resource
requires the configuration of an initial deployment id. We cannot create the blue/green deployment first as we need to 
control blue/green and canary settings after the stage creation. Changing this deployment with an additional deployment
resource would result in an inconsistent state in the template that associates multiple deployments with a stage. This
behaviour would be confusing. Hence, we manage the blue and the green stage in this resource.

_Q: How is this resource tested?_  
A: Unfortunately, the Python contract tests aren't running as of now (@see github issue [#112](https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/112)).
Therefore tests were done with the provided example deployment _example/infrastructure.yaml_.

_Q: What does the name SPRT stand for?_  
A: That's an easy one: *S*uper *P*eculiar *R*esource *T*ype.
