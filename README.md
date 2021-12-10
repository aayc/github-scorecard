After examining 27000 projects in Github, I found no correlation between OSSF Scorecard scores and repository stars.  Repositories with fewer stars often scored higher than repositories with more stars.  Here are some graphs that show this.

Looking at the highest rated repositories, there isn't an obvious trend that more popularity means higher ossf/scorecard scores.

Currently, there are 16 built-in checks in the ossf/scorecard project.  They are:

1) Binary-Artifacts: is the project free of checked-in binaries?
2) Branch-Protection: does the project use Branch Protection (i.e. only certain users can delete, push to branches)?
3) CI-Tests: does the project run tests in CI, e.g. Github Actions?
4) CII-Best-Practices: does the project have a CII best practices badge, (documentation, licenses, HTPS support, etc.)?
5) Code-Reiew: does the project require code review before code is merged?
6) Contributors: does the project have contirbutors from at least two different orgnaizations? (is score 10 or 0?)
7) Dependency-Update-Tool: does the project use tools to help update its dependencies?
8) Fuzzing: does the project use fuzzing, e.g. OSS-Fuzz?
9) Maintained: is the project maintained (highest score if at least one commit per week in past 90 days, lowest if archived)?)
10) Pinned-Dependencies: does the project declare and pin dependencies (i.e. explicitly versioning dependencies)?
11) Packaging: does the project build and publish official packages from CI/CD, e.g. Github publishing?
12) SAST: Does the project use static code analysis tools, e.g. CodeQL, SonarCloud?
13) Security-Policy: does the project contain a security policy (i.e., SECURITY.md which describes what constitutes a vulnerability and how to report it)?
14) Signed-Releases: does the project cryptographically sign releases?
15) Token-Permissions: does the project delcare Github workflow tokens as read only?
16) Vulnerabilities: does the project have unfixed vulnerabilities?

Similarly, two other projects in the same area include the SLSA project by Google, and the SAMM project by OWASP.  

The SLSA project defines four levels, with level 4 representing the ideal end state.  

Level 1 requires a build script and available provenance information for dependencies and builds, which offers a basic level of code source identification and can aid in vulnerability management.

Level 2 additionally requires version control, a build service, authenticated and service-generated provenance information.  This level prevents tampering to the extent that the build service is trusted.

Level 3 requires verified history, isolated and ephemeral build environments, and non-falsifiable provenance information.  This level provides much stronger protections against tampering than earlier levels, for example by preventing cross-build contamination

Lastly, level 4 requires two-person review, hermetic/reproducible/parameterless builds, complete dependency provenance information, which provides a high degree of confidence that the software has not been tampered with.

The SLSA project is in alpha stage with no public dataset or easily runnable artifacts.

The SAMM project similarly defines a Software Assurance Maturity Model which has 5 categories to consider when improving secure software practices
