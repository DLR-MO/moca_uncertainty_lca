# Checklist for Application Class 1 (markdown)
> The checklist is in version 1.1.1. It bases on the document QMH-DLR-VA005 in version 1.0.2.

## Usage Hints
This checklist provides recommendations for software development. It is primarily intended for software developers for the self-assessment of developed software and as a source of ideas for further development. The checklist does not provide any new, revolutionary approaches to software development. However, it helps to not forget necessary, essential steps of software development. In addition, the recommendations can serve as an argumentation aid. 

The recommendations are created with a focus on know-how maintenance and good software engineering practice. They help to maintain the sustainability of the developed software. The recommendations encourage the use of tools, the creation of documentation, the establishment of processes and adherence to principles. When assessing a recommendation, it is recommended to consider to what extent the aspect mentioned is implemented and whether there is a need for improvement. This could be implemented as follows: 

* Is there currently no need for improvement and is the recommendation addressed appropriately? Status: **ok** 
* Is there any potential for improvement that should be implemented in the near future? Status: **todo**, record the need for improvement 
* Is the recommendation not yet relevant but could be helpful in a later development phase? Status: **future** 
* Is the recommendation not meaningfully implementable within the development context? Status: **n.a.** (not applicable) explain the reason 

In case of questions, you can contact the Software Engineering Contact of your institute or facility.

> Please note the status between "[]" and list remarks below a recommendation.

## Summary of Results
The software uncertainty_lca implements 14 recommendations of application class 1. 

The focus of future improvements is on achieving readiness for publication on a public package index.

## Table of Contents
[[Qualification](#qualifizierung)] [[Requirements Management](#anforderungsmanagement)] [[Software Architecture](#software-architektur)] [[Change Management](#aenderungsmanagement)] [[Design and Implementation](#design-implementierung)] [[Software Test](#software-test)] [[Release Management](#release-management)] [[Automation and Dependency Management](#automatisierung-abhaengigkeiten)] 

## Qualification <a name="qualifizierung"></a>
**EQA.1** - **[ok]** The software responsible recognises the different application classes and knows which is to be used for his/her software. *(from application class 1)*

**EQA.2** - **[ok]** The software responsible knows how to request specific support at the beginning and during development as well as to exchange ideas with other colleagues on the subject of software development. *(from application class 1)*

**EQA.3** - **[ok]** The persons involved in the development determine the skills needed with regard to their role and the intended application class. They communicate these needs to the supervisor. *(from application class 1)*

**EQA.4** - **[ok]** The persons involved in the development are given the tools needed for their tasks and are trained in their use. *(from application class 1)*

## Requirements Management <a name="anforderungsmanagement"></a>
**EAM.1** - **[todo]** The problem definition is coordinated with all parties involved and documented. It describes the objectives, the purpose of the software, the essential requirements and the desired application class in a concise, understandable way. *(from application class 1)*

**EAM.3** - **[todo]** The constraints are documented. *(from application class 1)*

## Software Architecture <a name="software-architektur"></a>
**ESA.2** - **[todo]** Essential architectural concepts and corresponding decisions are at least documented in a lean way. *(from application class 1)*

## Change Management <a name="aenderungsmanagement"></a>
**EÄM.2** - **[todo]** The most important information describing how to contribute to development are stored in a central location. *(from application class 1)*

**EÄM.5** - **[ok]** Known bugs, important unresolved tasks and ideas are at least noted in bullet point form and stored centrally. *(from application class 1)*

> Gitlab issues are being used. They may not be quite up to date and miss most of what's in here, but they're being used.

**EÄM.7** - **[ok]** A repository is set up in a version control system. The repository is adequately structured and ideally contains all artefacts for building a usable software version and for testing it. *(from application class 1)*

**EÄM.8** - **[ok]** Every change of the repository ideally serves a specific purpose, contains an understandable description and leaves the software in a consistent, working state. *(from application class 1)*

> "every" may be a strong word in this context, but what gets pushed to main works most of the time.

## Design and Implementation <a name="design-implementierung"></a>
**EDI.1** - **[n.a.]** The usual patterns and solution approaches of the selected programming language are used and a set of rules regarding the programming style is consistently applied. The set of rules refers at least to the formatting and commenting. *(from application class 1)*

> This is mostly a single player proof of concept. So while the code is pythonic in a neat way, no specific set rules has been enforced or even chosen.

**EDI.2** - **[ok]** The software is structured modularly as far as possible. The modules are coupled loosely. I.e., a single module depends as little as possible on other modules. *(from application class 1)*

**EDI.9** - **[ok]** The source code and the comments contain as little duplicated information as possible. ("Don`t repeat yourself.") *(from application class 1)*

**EDI.10** - **[ok]** Prefer simple, understandable solutions. ("Keep it simple and stupid."). *(from application class 1)*

> See EDI.2

## Software Test <a name="software-test"></a>
**EST.4** - **[ok]** The basic functions and features of the software are tested in a near-operational environment. *(from application class 1)*

**EST.10** - **[todo]** The repository ideally contains all artefacts required to test the software. *(from application class 1)*

> It is not clear whether the MOCA_test_project.tar.gz should be published.

## Release Management <a name="release-management"></a>
**ERM.1** - **[ok]** Every release has a unique release number. The release number can be used to determine the underlying software version in the repository. *(from application class 1)*

> Ther version number is tracked in the `pyproject.toml` and managed via `bumpver`.

**ERM.2** - **[todo]** The release package contains or references the user documentation. At least, it consists of installation, usage and contact information as well as release notes. In the case of the distribution of the release package to third parties outside DLR, the licensing conditions must be enclosed. *(from application class 1)*

> Links to documentation are very dangly right now, release notes non existant.

**ERM.6** - **[todo]** All foreseen test activities are executed during release performance. *(from application class 1)*

**ERM.9** - **[ok]** Prior to distribution of the release package to third parties outside DLR, it must be ensured that a licence is defined, that the licensing terms of used third-party software are met, and that all necessary licence information is included in the release package. *(from application class 1)*

**ERM.10** - **[todo]** Prior to distribution of the release package to third parties outside DLR, it has to be ensured that the export control regulations are met. *(from application class 1)*

## Automation and Dependency Management <a name="automatisierung-abhaengigkeiten"></a>
**EAA.1** - **[todo]** The simple build process is basically automated and necessary manual steps are described. In addition, there is sufficient information available about the operational and development environment. *(from application class 1)*

**EAA.2** - **[ok]** The dependencies to build the software are at least described by name, version number, purpose, licensing terms and reference source. *(from application class 1)*

**EAA.10** - **[todo]** The repository ideally contains all artefacts to perform the build process. *(from application class 1)*

> With the test data being required for testing and the state of **EST.10**, this has to be sorted out.

> The checklist is in version 1.1.1. It bases on the document QMH-DLR-VA005 in version 1.0.2.
