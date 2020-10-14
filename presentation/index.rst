=========================================
AWS CDK vs Serverless framework vs TF CDK
=========================================

FIGHT!

Serverless framework
====================

The gateway drug

Pros
----

- Very easy to use
- Lot's of infrastructure with little code
- Healthy community
- Cloud agnostic (as if)

Cons
----

- Not that flexible
- `It's YAML <https://noyaml.com/>`_
- Plugins are incomplete and often out of date
- Bugs that are very hard to track down (EventBridge)

Code size
---------

68 lines of YAML

AWS CDK
=======

The big guns

Pros
----

- Write Python or some other, less relevant, languages (TypeScript, Java, and .NET)
- More easily reusable Constructs. Why write modules and nested stacks when you can write a class?
- String operations and other shenanigans withouth the joys of !Join
- IAM is a piece of cake

Cons
----

- Locked to AWS and CloudFormation (limited to 200 resources)
- Nested stacks are still bad, but at least more bearable

Code size
---------

109 lines of Python

Terraform CDK
=============

The new kid on the block

Pros
----

- It's terraform, but Python
- Cloud agnostic (even less, lol)
- Seems promising

Cons
----

- It's terraform, but Python
- v0.0.17
- IAM is a pain in the ass
- Lots of boiler code and manual work

Code size
---------

284 lines of Python
