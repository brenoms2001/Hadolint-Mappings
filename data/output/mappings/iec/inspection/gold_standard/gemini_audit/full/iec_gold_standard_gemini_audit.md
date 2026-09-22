# IEC 62443-3-3 Gemini Preliminary Audit

> **Important:** Gemini is used only as a preliminary auditor. Human review remains authoritative for the gold standard.

## Execution

- Model: `gemini-3.1-flash-lite`
- Prompt version: `iec-gemini-preliminary-audit-v3-enriched-context`
- Batch size: `5`
- Adaptive batch splitting: `True`
- Validation retries before split: `2`
- Input: `data/output/mappings/iec/inspection/gold_standard/iec_gold_standard_candidates.json`
- Input hash: `256b892b8c26213d9336c49473eb55af8eaeb8299062a64ee9b8a33f98044837`
- Standard: `IEC 62443-3-3`
- Matching threshold: `0.68`
- Matching Top-K: `10`
- Matching power: `5.5`
- Matching method: `cosine similarity -> clamp negative -> power transform -> L-infinity normalization -> threshold -> top-K`

## Summary

- Total candidates: **4134**
- YES: **78**
- MAYBE: **481**
- NO: **3575**
- Hadolint candidates: **529**
- ShellCheck candidates: **3605**
- Human-reviewed candidates: **0**

## Preliminary YES / MAYBE

### hadolint:DL1001:rank_4:SR 3.7

- Source rule: `DL1001` — Please refrain from using inline ignore pragmas # hadolint ignore=DLxxxx.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.894824`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration integrity and secure development

**Justification:** While the rule is about static analysis, preventing the suppression of warnings could theoretically prevent developers from ignoring security-related errors, which aligns loosely with the goal of secure error handling. However, the rule is not specific to error handling.

**Caveat:** The relationship is purely incidental based on the general goal of improving code quality.

### hadolint:DL1001:rank_7:SR 7.7

- Source rule: `DL1001` — Please refrain from using inline ignore pragmas # hadolint ignore=DLxxxx.
- Rank: `7`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.858662`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration management and least functionality

**Justification:** While the rule is about code quality, preventing the suppression of warnings could indirectly help ensure that security-related configurations (like disabling unnecessary services) are not bypassed by developers.

**Caveat:** The relationship is purely administrative and not a direct technical control for least functionality.

### hadolint:DL1001:rank_10:SR 5.2 RE 1

- Source rule: `DL1001` — Please refrain from using inline ignore pragmas # hadolint ignore=DLxxxx.
- Rank: `10`
- IEC target: `SR 5.2 RE 1` — Deny by default, allow by exception
- Relative score: `0.819172`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Policy enforcement

**Justification:** Similar to SR 7.7, the rule acts as a 'deny by default' mechanism for suppressing security checks. It ensures that security policies defined in the static analysis tool cannot be easily bypassed by developers.

**Caveat:** This is a meta-control (enforcing the enforcement tool) rather than a direct network traffic control.

### hadolint:DL3000:rank_10:SR 5.4

- Source rule: `DL3000` — Use absolute WORKDIR.
- Rank: `10`
- IEC target: `SR 5.4` — Application partitioning
- Relative score: `0.820691`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration hardening

**Justification:** While the rule is primarily for build stability, ensuring predictable file paths can be considered a minor aspect of maintaining a clean, partitioned container environment, though it does not directly implement application partitioning.

**Caveat:** The relationship is very weak and likely coincidental.

### hadolint:DL3001:rank_2:SR 3.2 RE 1

- Source rule: `DL3001` — Command does not make sense in a container.
- Rank: `2`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.89035`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Attack surface reduction

**Justification:** Removing dangerous utilities (like 'kill' or 'ifconfig') from a container reduces the tools available to an attacker if they gain execution, which aligns with the general goal of malicious code protection. However, it is not a direct implementation of a 'malicious code protection mechanism' at an entry/exit point.

**Caveat:** The relationship is based on general hardening rather than specific malicious code protection mechanisms.

### hadolint:DL3001:rank_9:SR 7.7

- Source rule: `DL3001` — Command does not make sense in a container.
- Rank: `9`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.753243`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `direct`

**Security objective:** Least functionality

**Justification:** The rule directly supports the principle of least functionality by removing unnecessary utilities (like top, nano, vim) from the container environment, thereby reducing the attack surface.

**Caveat:** The rule is a best practice for container hardening, which aligns well with the intent of SR 7.7.

### hadolint:DL3002:rank_6:SR 2.1 RE 1

- Source rule: `DL3002` — Last user should not be root.
- Rank: `6`
- IEC target: `SR 2.1 RE 1` — Authorization enforcement for all users
- Relative score: `0.778673`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Principle of Least Privilege`
- Directness: `Direct`

**Security objective:** Enforcement of least privilege for software processes

**Justification:** Running a container as a non-privileged user is a direct implementation of the principle of least privilege, which is the core objective of SR 2.1.

**Caveat:** The rule applies to container runtime configuration, while the requirement is broader, but the semantic alignment is strong.

### hadolint:DL3004:rank_4:SR 1.13 RE 1

- Source rule: `DL3004` — Do not use sudo.
- Rank: `4`
- IEC target: `SR 1.13 RE 1` — Explicit access request approval
- Relative score: `0.686417`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Access control and privilege management

**Justification:** Restricting sudo usage is a form of privilege management. While SR 1.13 RE 1 focuses on access requests via untrusted networks, both relate to the principle of least privilege and controlling administrative actions.

**Caveat:** The rule is a general best practice for container security, whereas the requirement is specific to network-based access requests.

### hadolint:DL3005:rank_1:SR 3.2

- Source rule: `DL3005` — Do not use apt-get dist-upgrade.
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity and configuration management

**Justification:** The rule aims to ensure image consistency and predictability by avoiding uncontrolled package upgrades. While this supports configuration management, it is only tangentially related to the malicious code protection mechanisms described in SR 3.2.

**Caveat:** The rule's rationale is explicitly noted as outdated and focuses on image reproducibility rather than security.

### hadolint:DL3005:rank_6:SR 7.7

- Source rule: `DL3005` — Do not use apt-get dist-upgrade.
- Rank: `6`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.877015`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** System hardening and minimization

**Justification:** While the rule is about package management, it relates to the broader concept of minimizing the attack surface of a container image, which aligns with the principle of least functionality.

**Caveat:** The rule is specifically about package upgrade strategies, not the removal of unnecessary services or protocols.

### hadolint:DL3008:rank_2:SR 7.7

- Source rule: `DL3008` — Pin versions in apt-get install.
- Rank: `2`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.903905`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software supply chain integrity and configuration management

**Justification:** While version pinning is primarily for reproducibility, it indirectly supports least functionality by preventing the accidental installation of unnecessary or vulnerable package versions that might introduce unwanted services.

**Caveat:** The primary intent of the rule is build stability, not the restriction of system functions.

### hadolint:DL3008:rank_5:SR 3.2

- Source rule: `DL3008` — Pin versions in apt-get install.
- Rank: `5`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.761448`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Software integrity and supply chain security

**Justification:** Pinning versions prevents the accidental introduction of malicious or vulnerable code via unexpected package updates, which aligns with the goal of preventing unauthorized software changes.

**Caveat:** This is a configuration best practice rather than a direct 'malicious code protection' mechanism as defined in the standard.

### hadolint:DL3009:rank_1:SR 4.2

- Source rule: `DL3009` — Delete the apt-get lists after installing something.
- Rank: `1`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Information leakage prevention

**Justification:** Cleaning up apt lists prevents the leakage of package metadata, which aligns with the spirit of preventing information disclosure, though SR 4.2 specifically targets decommissioning and shared memory.

**Caveat:** The requirement is focused on decommissioning/purging, while the rule is focused on image size and hygiene.

### hadolint:DL3011:rank_4:SR 7.7

- Source rule: `DL3011` — Valid UNIX ports range from 0 to 65535.
- Rank: `4`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.735764`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `indirect`

**Security objective:** Least functionality

**Justification:** Restricting ports to valid ranges is a prerequisite for managing and restricting services, which aligns with the objective of limiting unnecessary ports and services.

**Caveat:** The rule is a basic validation check, while SR 7.7 is a broader architectural requirement.

### hadolint:DL3012:rank_1:SR 3.2

- Source rule: `DL3012` — Multiple HEALTHCHECK instructions
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `supportive`
- Directness: `indirect`

**Security objective:** Malicious code protection

**Justification:** HEALTHCHECK instructions are used to monitor container health; ensuring they are configured correctly can help detect if a container has been compromised or is malfunctioning, which is a component of detection.

**Caveat:** The rule is primarily about configuration hygiene rather than a security-specific protection mechanism.

### hadolint:DL3012:rank_3:SR 3.3 RE 1

- Source rule: `DL3012` — Multiple HEALTHCHECK instructions
- Rank: `3`
- IEC target: `SR 3.3 RE 1` — Automated mechanisms for security functionality verification
- Relative score: `0.822315`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Automated verification

**Justification:** While the rule is about Docker configuration, a HEALTHCHECK is an automated mechanism for verifying service health. It is tangentially related to the broader concept of automated verification, though not specifically for security functions as required by SR 3.3.

**Caveat:** The rule is primarily for operational health, not security verification.

### hadolint:DL3012:rank_5:SR 3.3

- Source rule: `DL3012` — Multiple HEALTHCHECK instructions
- Rank: `5`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.786934`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Security functionality verification

**Justification:** Similar to the RE 1 case, a HEALTHCHECK is an automated check. If the health check were specifically monitoring a security function, it could support SR 3.3, but the rule itself is generic.

**Caveat:** The rule is too generic to be considered a direct implementation of SR 3.3.

### hadolint:DL3012:rank_6:SR 7.7

- Source rule: `DL3012` — Multiple HEALTHCHECK instructions
- Rank: `6`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.767022`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Least functionality

**Justification:** The rule prevents redundant instructions, which aligns loosely with the principle of minimizing unnecessary configuration, but it does not address the restriction of functions, ports, or services as defined in SR 7.7.

**Caveat:** The rule is about configuration syntax, not the restriction of system services.

### hadolint:DL3013:rank_1:SR 3.2

- Source rule: `DL3013` — Pin versions in pip.
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Supply chain integrity and malicious code prevention

**Justification:** Pinning versions in pip helps ensure the integrity of the software supply chain by preventing the accidental introduction of malicious or compromised code updates, which aligns with the goal of preventing unauthorized software.

**Caveat:** Version pinning is a best practice for stability and integrity, but it is not a direct 'malicious code protection' mechanism as defined by the standard (e.g., antivirus, whitelisting).

### hadolint:DL3015:rank_1:SR 7.7

- Source rule: `DL3015` — Avoid additional packages by specifying --no-install-recommends.
- Rank: `1`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Supportive`
- Directness: `Direct`

**Security objective:** Least functionality

**Justification:** By restricting installed packages to only those explicitly required, the rule directly supports the principle of least functionality by reducing the attack surface and removing unnecessary services or binaries.

**Caveat:** This is a configuration-level control that contributes to the overall system hardening required by SR 7.7.

### hadolint:DL3015:rank_3:SR 2.4

- Source rule: `DL3015` — Avoid additional packages by specifying --no-install-recommends.
- Rank: `3`
- IEC target: `SR 2.4` — Mobile code
- Relative score: `0.763035`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Mobile code restriction

**Justification:** While reducing installed packages can limit the presence of interpreters or tools that might execute mobile code, the rule does not specifically address mobile code technologies as defined in SR 2.4.

**Caveat:** The relationship is incidental rather than a direct control for mobile code.

### hadolint:DL3016:rank_10:SR 7.6

- Source rule: `DL3016` — Pin versions in npm.
- Rank: `10`
- IEC target: `SR 7.6` — Network and security configuration settings
- Relative score: `0.682696`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Configuration management and integrity

**Justification:** Version pinning ensures that the software environment matches a known, approved configuration. This aligns loosely with the objective of maintaining a controlled and auditable system configuration, though SR 7.6 is more focused on network/security parameters.

**Caveat:** The rule is a build-time practice, while SR 7.6 typically refers to runtime configuration settings.

### hadolint:DL3017:rank_4:SR 7.7

- Source rule: `DL3017` — Do not use apk upgrade
- Rank: `4`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.837061`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Least functionality

**Justification:** While the rule is about package management, avoiding unnecessary upgrades can be seen as a form of maintaining a minimal, predictable, and stable software baseline, which aligns with the spirit of least functionality.

**Caveat:** The rule is primarily about build reproducibility and stability rather than explicitly restricting services or protocols.

### hadolint:DL3018:rank_6:SR 3.3

- Source rule: `DL3018` — Pin versions in apk add
- Rank: `6`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.684781`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software supply chain integrity and configuration management

**Justification:** While version pinning is primarily for build stability, it can be considered a form of configuration control that supports the integrity of the software environment, which is a prerequisite for verifying security functions. However, it is not a direct verification mechanism for security functions as described in SR 3.3.

**Caveat:** The relationship is very weak and likely represents a false positive in automated matching.

### hadolint:DL3019:rank_5:SR 7.7

- Source rule: `DL3019` — Use the --no-cache switch
- Rank: `5`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.791889`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Least functionality and attack surface reduction

**Justification:** While the rule is primarily for image optimization, removing unnecessary packages (which might be cached) aligns loosely with the principle of least functionality by reducing the installed software footprint.

**Caveat:** The rule is primarily an optimization/maintenance rule, not a security-focused hardening rule.

### hadolint:DL3020:rank_2:SR 3.4

- Source rule: `DL3020` — Use COPY instead of ADD for files and folders
- Rank: `2`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.850205`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity

**Justification:** While DL3020 is primarily a build-time best practice, using ADD can lead to unexpected file behavior (like auto-extraction of archives), which could theoretically be exploited to bypass integrity checks if not carefully managed. However, this is a stretch.

**Caveat:** The rule is a build-time configuration best practice, not a runtime integrity protection mechanism.

### hadolint:DL3020:rank_3:SR 3.2

- Source rule: `DL3020` — Use COPY instead of ADD for files and folders
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.70373`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Malicious code protection

**Justification:** The use of ADD can potentially introduce malicious code via auto-extracted archives if the source is compromised. Using COPY is safer, but this is a preventative build-time practice rather than a comprehensive malicious code protection mechanism.

**Caveat:** This is a preventative coding practice, not a security control mechanism as described in SR 3.2.

### hadolint:DL3025:rank_1:SR 3.2 RE 1

- Source rule: `DL3025` — Use arguments JSON notation for CMD and ENTRYPOINT arguments
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Supportive`
- Directness: `Direct`

**Security objective:** System availability and process control integrity

**Justification:** The rule ensures that the containerized application receives OS signals (like SIGTERM) correctly. This is critical for the graceful shutdown and reliable management of control system processes, which supports the requirement for maintaining control system integrity at entry/exit points.

**Caveat:** The rule is a best practice for container orchestration, which indirectly supports the broader requirement of malicious code protection by ensuring the system remains in a predictable, manageable state.

### hadolint:DL3025:rank_3:SR 3.7

- Source rule: `DL3025` — Use arguments JSON notation for CMD and ENTRYPOINT arguments
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.836842`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Error handling

**Justification:** Ensuring signals are passed correctly allows the application to handle termination signals properly, which is a form of error/lifecycle management. However, this is not the primary focus of the rule.

**Caveat:** The rule is about process lifecycle management, not the security-sensitive handling of error conditions or information disclosure.

### hadolint:DL3025:rank_4:SR 3.3 RE 2

- Source rule: `DL3025` — Use arguments JSON notation for CMD and ENTRYPOINT arguments
- Rank: `4`
- IEC target: `SR 3.3 RE 2` — Security functionality verification during normal operation
- Relative score: `0.777953`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Security functionality verification

**Justification:** Proper signal handling ensures the container behaves as expected during lifecycle events, which is a prerequisite for reliable operation, but it does not directly verify security functions.

**Caveat:** The relationship is purely operational and does not address the verification of security-specific functions.

### hadolint:DL3026:rank_2:SR 5.2 RE 1

- Source rule: `DL3026` — Use only an allowed registry in the FROM image
- Rank: `2`
- IEC target: `SR 5.2 RE 1` — Deny by default, allow by exception
- Relative score: `0.697656`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `analogous`
- Directness: `indirect`

**Security objective:** Supply chain security and image provenance

**Justification:** While the rule is about image provenance, the concept of 'trusted registry' acts as an allow-list, which is conceptually similar to the 'deny by default, allow by exception' principle in network traffic management.

**Caveat:** The rule applies to software supply chain, not network traffic.

### hadolint:DL3028:rank_3:SR 3.2

- Source rule: `DL3028` — Pin versions in gem install
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.76187`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software supply chain integrity

**Justification:** Version pinning can prevent the accidental introduction of malicious code via compromised upstream dependencies, which aligns with the broad goal of malicious code protection.

**Caveat:** This is a preventative measure for supply chain security, not a direct malicious code detection or mitigation mechanism as described in SR 3.2.

### hadolint:DL3031:rank_1:SR 3.2

- Source rule: `DL3031` — Do not use yum update
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software configuration management

**Justification:** The rule discourages 'yum update' to ensure build consistency and avoid failures. While this relates to software configuration management, it is not directly about malicious code protection mechanisms as defined in SR 3.2.

**Caveat:** The rule is a best practice for build reproducibility, not a security control for malicious code.

### hadolint:DL3033:rank_1:SR 3.2

- Source rule: `DL3033` — Specify version with yum install -y <package>-<version>
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Supply chain integrity and malicious code prevention

**Justification:** Version pinning helps ensure that known, vetted software versions are deployed, which is a foundational practice for preventing the accidental introduction of malicious or vulnerable code.

**Caveat:** While version pinning is a best practice for integrity, it is not a direct implementation of the malicious code protection mechanisms (like AV or sandboxing) described in SR 3.2.

### hadolint:DL3034:rank_2:SR 3.7

- Source rule: `DL3034` — Non-interactive switch missing from zypper command: zypper install -y
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.918464`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and process reliability

**Justification:** The rule prevents a build failure due to an unhandled interactive prompt, which is a form of error handling, but it does not address the security-sensitive error handling described in SR 3.7.

**Caveat:** The scope of SR 3.7 is specifically about preventing information leakage during error conditions, which is not addressed by this rule.

### hadolint:DL3035:rank_1:SR 3.2

- Source rule: `DL3035` — Do not use zypper update
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `indirect`

**Security objective:** Malicious code protection

**Justification:** The rule encourages specific package management and patching (e.g., --cve), which supports the requirement to mitigate malicious code and maintain updated protection mechanisms.

**Caveat:** The rule is primarily for build reproducibility, but its recommendation to use 'zypper patch' directly supports vulnerability mitigation.

### hadolint:DL3037:rank_1:SR 3.2

- Source rule: `DL3037` — Specify version with zypper install -y <package>[=]<version>
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Software integrity and supply chain security

**Justification:** Version pinning helps ensure that the software installed is the intended, tested version, which supports the integrity aspect of malicious code protection by preventing the accidental introduction of unverified or compromised package updates.

**Caveat:** This is a configuration best practice for reproducibility rather than a direct malicious code protection mechanism.

### hadolint:DL3037:rank_5:SR 2.4 RE 1

- Source rule: `DL3037` — Specify version with zypper install -y <package>[=]<version>
- Rank: `5`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.910934`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Software integrity

**Justification:** While version pinning ensures a specific version is used, it is not a substitute for cryptographic integrity verification (e.g., checksums or signatures) required for mobile code.

**Caveat:** Version pinning is a poor proxy for integrity checks and should not be conflated with cryptographic verification.

### hadolint:DL3037:rank_9:SR 3.4

- Source rule: `DL3037` — Specify version with zypper install -y <package>[=]<version>
- Rank: `9`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.787471`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Software integrity

**Justification:** While version pinning is primarily for reproducibility, it indirectly supports integrity by ensuring that the software components installed are known and expected, reducing the risk of unexpected or malicious package updates.

**Caveat:** This is a best practice for configuration management, not a direct integrity verification mechanism like cryptographic hashing.

### hadolint:DL3039:rank_3:SR 3.2

- Source rule: `DL3039` — Do not use dnf update
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.750517`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity and maintenance

**Justification:** While the rule is primarily for image size, keeping packages updated or consistent can be a minor part of maintaining a secure software environment, which relates to malicious code protection.

**Caveat:** The rule is not a security control for malicious code protection.

### hadolint:DL3040:rank_1:SR 4.2

- Source rule: `DL3040` — dnf clean all missing after dnf command.
- Rank: `1`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Data sanitization and information persistence

**Justification:** Cleaning cached data is a form of data removal, which is conceptually similar to purging information, though the rule is intended for storage optimization rather than security sanitization.

**Caveat:** The rule is for image size optimization, not for security-critical data sanitization.

### hadolint:DL3041:rank_2:SR 3.2

- Source rule: `DL3041` — Specify version with dnf install -y <package>-<version>
- Rank: `2`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.964002`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Software integrity and supply chain security

**Justification:** Version pinning helps ensure the integrity of the software stack by preventing the accidental introduction of unverified or malicious package updates, which aligns with the broader goal of preventing unauthorized software, though it is not a direct malicious code detection mechanism.

**Caveat:** Version pinning is a configuration management best practice rather than a direct malicious code protection mechanism as defined in SR 3.2.

### hadolint:DL3041:rank_8:SR 7.6

- Source rule: `DL3041` — Specify version with dnf install -y <package>-<version>
- Rank: `8`
- IEC target: `SR 7.6` — Network and security configuration settings
- Relative score: `0.758809`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration management

**Justification:** Version pinning ensures that the software environment matches a known, approved configuration. This aligns with the goal of maintaining consistent security configurations, though the rule is more about build reproducibility than runtime configuration monitoring.

**Caveat:** The rule is a build-time practice, while SR 7.6 focuses on runtime configuration settings.

### hadolint:DL3041:rank_9:SR 3.4

- Source rule: `DL3041` — Specify version with dnf install -y <package>-<version>
- Rank: `9`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.738792`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity

**Justification:** Version pinning helps ensure that the software installed is the intended version, which is a prerequisite for maintaining integrity. However, it does not provide the detection or protection mechanisms against unauthorized changes required by SR 3.4.

**Caveat:** Version pinning is a preventative measure for consistency, not an integrity monitoring mechanism.

### hadolint:DL3043:rank_6:SR 3.7

- Source rule: `DL3043` — DL3043
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.880779`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule identifies syntax errors in Dockerfiles. While this is a form of error detection, it is a build-time syntax check rather than the runtime error handling and information disclosure prevention required by SR 3.7.

**Caveat:** The rule is a static analysis check for build files, whereas SR 3.7 focuses on runtime system behavior.

### hadolint:DL3044:rank_1:SR 3.7

- Source rule: `DL3044` — DL3044
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and configuration reliability

**Justification:** The rule identifies a configuration error that leads to unexpected behavior (variable expansion failure). While this is an error condition, it is a development-time configuration issue rather than an operational error handling mechanism intended to prevent information disclosure to adversaries.

**Caveat:** The rule improves system reliability, which is a prerequisite for secure operation, but it does not directly address the security-specific requirements of SR 3.7 regarding error message disclosure.

### hadolint:DL3048:rank_3:SR 3.5

- Source rule: `DL3048` — Invalid Label Key
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.91589`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule validates the syntax of a configuration input (label key), it is a static configuration check rather than a runtime input validation mechanism for industrial process control inputs as required by SR 3.5.

**Caveat:** The rule validates static configuration syntax, which is a form of input validation, but it does not address the security of process control inputs.

### hadolint:DL3050:rank_1:SR 7.7

- Source rule: `DL3050` — Superfluous label(s) present.
- Rank: `1`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Information leakage prevention vs Least functionality

**Justification:** Removing superfluous labels can reduce information leakage, which aligns with the principle of least functionality by minimizing the footprint of the container, though it is not a direct control for services/ports.

**Caveat:** The rule is primarily about metadata hygiene rather than disabling active services or protocols.

### hadolint:DL3050:rank_2:SR 3.7

- Source rule: `DL3050` — Superfluous label(s) present.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.774855`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Information leakage prevention vs Error handling

**Justification:** Superfluous labels might contain information that could be exploited by an adversary, which aligns with the goal of SR 3.7 to prevent information disclosure, though the rule is not specifically about error handling.

**Caveat:** The rule is a preventative measure for information disclosure, but it does not address the handling of error conditions.

### hadolint:DL3053:rank_1:SR 2.11

- Source rule: `DL3053` — Label <label> is not a valid time format - must be conform to RFC3339.
- Rank: `1`
- IEC target: `SR 2.11` — Timestamps
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Auditability and time synchronization

**Justification:** The rule enforces a standard format for timestamps in container labels, which supports the consistency required for audit records mentioned in SR 2.11.

**Caveat:** The rule applies to container metadata, not the control system's internal clock or audit logging mechanism itself.

### hadolint:DL3054:rank_3:SR 3.2

- Source rule: `DL3054` — Label <label> is not a valid SPDX license identifier.
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.841845`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** Ensuring software is properly licensed and identified can be a component of software provenance, which is a prerequisite for verifying the integrity of software to prevent malicious code.

**Caveat:** The rule is primarily for license compliance, not security-focused integrity verification.

### hadolint:DL3054:rank_7:SR 3.4

- Source rule: `DL3054` — Label <label> is not a valid SPDX license identifier.
- Rank: `7`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.771346`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software and information integrity

**Justification:** While the rule is primarily for license compliance, ensuring metadata is standardized and machine-readable can be considered a minor aspect of software supply chain integrity, which is a component of SR 3.4.

**Caveat:** The rule does not provide actual integrity protection (e.g., cryptographic hashes) as required by SR 3.4.

### hadolint:DL3055:rank_1:SR 2.12 RE 1

- Source rule: `DL3055` — Label <label> is not a valid git hash.
- Rank: `1`
- IEC target: `SR 2.12 RE 1` — Non-repudiation for all users
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect support`
- Directness: `indirect`

**Security objective:** Software provenance and traceability

**Justification:** Including a git hash in a container label provides traceability for the software version, which supports non-repudiation by allowing auditors to link a specific container image to a specific source code commit.

**Caveat:** This is a metadata-level support for traceability, not a direct implementation of user-action non-repudiation.

### hadolint:DL3055:rank_4:SR 2.4 RE 1

- Source rule: `DL3055` — Label <label> is not a valid git hash.
- Rank: `4`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.928306`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect support`
- Directness: `indirect`

**Security objective:** Software provenance and integrity

**Justification:** While a git hash can be used to verify the origin of code, it is not a cryptographic integrity check for mobile code execution as required by SR 2.4.

**Caveat:** A git hash is a reference, not a cryptographic signature or integrity verification mechanism.

### hadolint:DL3055:rank_7:SR 3.2

- Source rule: `DL3055` — Label <label> is not a valid git hash.
- Rank: `7`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.853549`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity and supply chain security

**Justification:** While the rule is primarily for traceability, using git hashes can support integrity verification (a component of malicious code protection). However, it does not directly prevent or detect malicious code.

**Caveat:** The rule is a best practice for provenance, not a direct security control for malicious code.

### hadolint:DL3056:rank_3:SR 3.2

- Source rule: `DL3056` — Label <label> does not conform to semantic versioning.
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.732161`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity and lifecycle management

**Justification:** While semantic versioning is not a direct malicious code protection mechanism, knowing the version of software is a prerequisite for vulnerability management and ensuring that authorized/patched software is running.

**Caveat:** The rule is a best practice for configuration, not a security control for malicious code protection.

### hadolint:DL3057:rank_1:SR 3.2

- Source rule: `DL3057` — HEALTHCHECK instruction missing.
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** System health monitoring

**Justification:** HEALTHCHECK provides a mechanism to detect if a service is running correctly. While not a direct malicious code protection mechanism, it can be used to detect anomalies or service failures that might indicate a compromise or malicious activity.

**Caveat:** The rule is often used for operational availability rather than security, and its effectiveness depends on the implementation of the health check script.

### hadolint:DL3057:rank_2:SR 3.3

- Source rule: `DL3057` — HEALTHCHECK instruction missing.
- Rank: `2`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.945852`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Verification of security functions

**Justification:** A health check can be part of a verification strategy to ensure that a containerized service is operating as expected, which aligns with the broader goal of verifying security functions.

**Caveat:** HEALTHCHECK is primarily an operational tool; it is not a dedicated security verification function as described in SR 3.3.

### hadolint:DL3057:rank_3:SR 3.3 RE 1

- Source rule: `DL3057` — HEALTHCHECK instruction missing.
- Rank: `3`
- IEC target: `SR 3.3 RE 1` — Automated mechanisms for security functionality verification
- Relative score: `0.927367`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Automated verification

**Justification:** The HEALTHCHECK instruction is an automated mechanism that can be used to monitor the status of a service, which is a form of automated verification of operational state.

**Caveat:** This is an operational check, not a security-specific verification mechanism.

### hadolint:DL3057:rank_9:SR 3.3 RE 2

- Source rule: `DL3057` — HEALTHCHECK instruction missing.
- Rank: `9`
- IEC target: `SR 3.3 RE 2` — Security functionality verification during normal operation
- Relative score: `0.692279`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Verification of security functions

**Justification:** While a health check is primarily for operational availability, it can be interpreted as a mechanism to verify that a service (which may include security functions) is running as intended.

**Caveat:** The rule is a general operational check, not specifically a security function verification.

### hadolint:DL3057:rank_10:SR 3.2 RE 1

- Source rule: `DL3057` — HEALTHCHECK instruction missing.
- Rank: `10`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.688833`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** System integrity and availability

**Justification:** A HEALTHCHECK can be considered a mechanism to monitor the health of a container, which is a form of entry/exit point monitoring, but the rule is primarily for operational reliability rather than malicious code protection.

**Caveat:** The rule is disabled by default and is more focused on operational health than security.

### hadolint:DL3059:rank_1:SR 4.2

- Source rule: `DL3059` — Multiple consecutive RUN instructions. Consider consolidation.
- Rank: `1`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Information persistence

**Justification:** Consolidating RUN commands can prevent sensitive temporary files from persisting in intermediate image layers, which aligns with the goal of preventing unauthorized information disclosure.

**Caveat:** The primary intent of the rule is image size optimization, not security-focused data purging.

### hadolint:DL3060:rank_1:SR 4.2

- Source rule: `DL3060` — yarn cache clean missing after yarn install was run.
- Rank: `1`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Data minimization and cleanup

**Justification:** While the rule is primarily for image size optimization, clearing caches can be considered a form of data hygiene that prevents unnecessary information persistence in the container image, which aligns loosely with the intent of SR 4.2.

**Caveat:** The rule is not intended for security, but for storage efficiency.

### hadolint:DL3062:rank_1:SR 3.2

- Source rule: `DL3062` — Problematic code:
- Rank: `1`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `preventative`
- Directness: `indirect`

**Security objective:** Supply chain integrity and malicious code prevention

**Justification:** Pinning dependencies prevents the accidental or malicious introduction of unauthorized code (e.g., supply chain attacks), which aligns with the objective of preventing unauthorized software execution.

**Caveat:** This is a development-time practice that supports the overall objective of malicious code protection but is not a direct runtime protection mechanism.

### hadolint:DL3062:rank_2:SR 3.2 RE 1

- Source rule: `DL3062` — Problematic code:
- Rank: `2`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.958751`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `preventative`
- Directness: `indirect`

**Security objective:** Supply chain integrity

**Justification:** While version pinning helps ensure the integrity of software entering the system, the requirement specifically targets entry/exit points (e.g., network gateways, USB ports). The link is weak.

**Caveat:** The rule applies to build-time dependencies, whereas the requirement focuses on runtime traffic or data entry points.

### hadolint:DL3062:rank_4:SR 2.4

- Source rule: `DL3062` — Problematic code:
- Rank: `4`
- IEC target: `SR 2.4` — Mobile code
- Relative score: `0.80157`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Mobile code control

**Justification:** While version pinning helps ensure the provenance of code, SR 2.4 specifically targets mobile code technologies (e.g., JavaScript, ActiveX). If the 'go' packages are considered mobile code, this rule could be a partial control for origin verification.

**Caveat:** The rule is a general build-time practice, not a runtime mobile code restriction mechanism.

### hadolint:DL3062:rank_5:SR 2.4 RE 1

- Source rule: `DL3062` — Problematic code:
- Rank: `5`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.789596`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Mobile code integrity

**Justification:** Version pinning acts as a form of integrity check by ensuring the same code is used consistently. However, it is not a cryptographic integrity verification mechanism as typically required by SR 2.4 RE 1.

**Caveat:** Version pinning is a configuration management practice, not a cryptographic integrity check.

### hadolint:DL3063:rank_10:SR 7.7

- Source rule: `DL3063` — Stage name should not be a reserved word
- Rank: `10`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.711983`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration hardening

**Justification:** While the rule is a simple naming check, it relates to the broader concept of 'least functionality' by ensuring that build configurations are clean and follow expected standards, which is a minor aspect of system hardening.

**Caveat:** The relationship is very weak as the rule does not restrict functions, ports, or services.

### hadolint:DL3064:rank_7:SR 4.1

- Source rule: `DL3064` — Potentially sensitive data should not be used in the ARG or ENV commands
- Rank: `7`
- IEC target: `SR 4.1` — Information confidentiality
- Relative score: `0.786912`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supporting`
- Directness: `direct`

**Security objective:** Information confidentiality

**Justification:** Preventing sensitive data (like credentials) from being persisted in container images is a direct measure to maintain the confidentiality of information.

**Caveat:** The rule is specific to container build-time security, while the requirement is broader.

### hadolint:DL4000:rank_3:SR 7.6 RE 1

- Source rule: `DL4000` — MAINTAINER is deprecated
- Rank: `3`
- IEC target: `SR 7.6 RE 1` — Machine-readable reporting of current security settings
- Relative score: `0.821522`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Machine-readable reporting of security settings

**Justification:** While the rule encourages using standard OCI labels (machine-readable metadata), it is a stretch to equate this to the requirement for reporting security settings.

**Caveat:** The use of standard labels could theoretically be part of a broader system inventory, but the rule itself is not a security setting report.

### hadolint:DL4006:rank_1:SR 5.2 RE 3

- Source rule: `DL4006` — Set the SHELL option -o pipefail before RUN with a pipe in
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Fail close / Error handling

**Justification:** While 'pipefail' ensures a build fails if a command fails, this is a build-time integrity check, not a runtime boundary protection mechanism as defined in SR 5.2.

**Caveat:** The rule improves build reliability, which is a prerequisite for secure software, but it does not implement the 'fail close' requirement for communication boundaries.

### shellcheck:SC1000:rank_1:SR 3.5

- Source rule: `SC1000` — SC1000
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and sanitization

**Justification:** The rule enforces correct escaping of special characters in shell scripts to prevent unintended interpretation. While this is a form of syntax validation, SR 3.5 specifically targets industrial process control inputs. The rule is a general coding best practice rather than a specific control system input validation mechanism.

**Caveat:** The rule is a general-purpose coding standard; its application to industrial control systems is indirect.

### shellcheck:SC1001:rank_1:SR 3.5

- Source rule: `SC1001` — This \o will be a regular 'o' in this context.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC1001 is primarily a syntax/style warning about unnecessary backslashes, it touches on how characters are interpreted by the shell. SR 3.5 requires validating input to prevent it from being unintentionally interpreted as commands. The rule is tangentially related to ensuring input is interpreted as intended, but it is not a security-focused input validation rule.

**Caveat:** The rule is a code quality/style check rather than a security-critical input validation check.

### shellcheck:SC1003:rank_1:SR 3.5

- Source rule: `SC1003` — Want to escape a single quote? echo 'This is how it'\''s done'.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and sanitization

**Justification:** SC1003 addresses shell quoting syntax, which is a form of input handling. SR 3.5 requires input validation to prevent injection attacks. While SC1003 is a syntax warning, proper quoting is a fundamental prerequisite for preventing command injection, which is explicitly mentioned in the SR 3.5 rationale.

**Caveat:** The rule is primarily a syntax linter rather than a security-focused input validation check.

### shellcheck:SC1004:rank_1:SR 3.5

- Source rule: `SC1004` — This backslash+linefeed is literal. Break outside single quotes if you just want to break the line.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_correctness_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation and sanitization

**Justification:** While SC1004 is primarily a syntax/formatting warning, the rationale for SR 3.5 mentions that inputs passed to interpreters should be pre-screened to prevent unintended interpretation. Ensuring correct string literal handling is a prerequisite for robust input processing.

**Caveat:** The rule is primarily about code style/syntax rather than security-critical input validation.

### shellcheck:SC1008:rank_1:SR 3.3

- Source rule: `SC1008` — This shebang was unrecognized. ShellCheck only supports sh/bash/dash/ksh. Add a 'shell' directive to specify.
- Rank: `1`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Security functionality verification

**Justification:** The rule ensures the shell environment is correctly identified, which is a prerequisite for reliable execution of scripts. While not a security function itself, ensuring scripts run in the intended environment is a minor aspect of configuration management for security tools.

**Caveat:** This is a very weak link; the rule is primarily about developer tooling rather than security verification.

### shellcheck:SC1011:rank_1:SR 3.5

- Source rule: `SC1011` — This apostrophe terminated the single quoted string!
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule addresses syntax errors in shell scripts (quoting). While this is a form of 'input' to the shell interpreter, it is primarily a functional correctness issue rather than a security-focused input validation requirement as defined in SR 3.5.

**Caveat:** If the shell script processes untrusted user input, improper quoting could lead to command injection, which would then fall under SR 3.5.

### shellcheck:SC1012:rank_1:SR 3.5

- Source rule: `SC1012` — \t is just literal t here. For tab, use "$(printf '\t')" instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule addresses incorrect escape sequences in shell scripts. Similar to SC1011, this is primarily a functional correctness issue, though it relates to how data is interpreted by the shell.

**Caveat:** If the script handles external data, ensuring correct interpretation is a prerequisite for secure input handling, but the rule itself is not a security control.

### shellcheck:SC1014:rank_2:SR 3.7

- Source rule: `SC1014` — Use if cmd; then .. to check exit code, or if [ "$(cmd)" = .. ] to check output.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.904805`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule addresses incorrect usage of shell commands that could lead to unexpected script behavior or failure to detect errors, which is tangentially related to robust error handling.

**Caveat:** The rule is a syntax/best-practice check, not a security-specific error handling mechanism.

### shellcheck:SC1014:rank_4:SR 3.5

- Source rule: `SC1014` — Use if cmd; then .. to check exit code, or if [ "$(cmd)" = .. ] to check output.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.84299`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and correct command execution

**Justification:** The rule prevents syntax errors in shell scripts that could lead to unintended command execution or logic bypasses. While not a direct input validation of external data, it ensures that conditional logic (which often processes inputs) is executed as intended, aligning with the goal of preventing malformed commands.

**Caveat:** The rule is primarily a code quality/correctness check rather than a security-focused input validation mechanism.

### shellcheck:SC1015:rank_1:SR 3.5

- Source rule: `SC1015` — This is a Unicode double quote. Delete and retype it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax/formatting issue, using incorrect character encodings (Unicode quotes) can lead to unexpected behavior or bypasses in interpreters, which touches upon the broader concept of input validation.

**Caveat:** The rule is primarily a linter warning for developer convenience rather than a security-focused input validation check.

### shellcheck:SC1016:rank_1:SR 3.5

- Source rule: `SC1016` — This is a Unicode single quote. Delete and retype it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** Similar to SC1015, this rule addresses character encoding issues that could potentially cause unexpected interpretation of input, which is relevant to the scope of input validation.

**Caveat:** The rule is primarily a linter warning for developer convenience rather than a security-focused input validation check.

### shellcheck:SC1017:rank_1:SR 3.5

- Source rule: `SC1017` — Literal carriage return. Run script through tr -d '\r' .
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `input_sanitization`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** SC1017 ensures scripts are free of carriage returns that can cause unexpected behavior or command misinterpretation. While primarily a portability issue, it aligns with the spirit of ensuring inputs (scripts) are in a valid, expected format to prevent unintended execution behavior.

**Caveat:** This is a weak association as the rule is primarily for portability rather than security-focused input validation.

### shellcheck:SC1020:rank_1:SR 3.5

- Source rule: `SC1020` — You need a space before the ] or ]]
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `code_correctness_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule is a syntax check for shell scripts, ensuring correct syntax in scripts that process inputs can prevent logic errors that might lead to improper input handling. However, it is a general code quality rule rather than a security-specific input validation mechanism.

**Caveat:** The rule is primarily for code correctness, not security-focused input validation.

### shellcheck:SC1026:rank_1:SR 3.5

- Source rule: `SC1026` — If grouping expressions inside [[..]], use ( .. ).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Defensive Coding`
- Directness: `Indirect`

**Security objective:** Input validation

**Justification:** The rule enforces correct syntax for conditional expressions in shell scripts. While this improves code reliability and prevents logic errors, it is a general coding best practice rather than a specific security control for validating external inputs as required by SR 3.5.

**Caveat:** The rule prevents undefined behavior in shell scripts, which could theoretically lead to unexpected execution paths, but it is not a primary input validation mechanism.

### shellcheck:SC1027:rank_2:SR 3.7

- Source rule: `SC1027` — Expected another argument for this operator.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.858236`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** While SC1027 is a syntax error, improper handling of shell script errors can lead to unexpected behavior. However, this rule is a static analysis check for developer error, not a runtime error handling mechanism for security.

**Caveat:** The rule is a static check, whereas SR 3.7 focuses on runtime error handling and information disclosure.

### shellcheck:SC1027:rank_4:SR 3.5

- Source rule: `SC1027` — Expected another argument for this operator.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.731154`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** SC1027 detects a malformed test expression. While not strictly input validation, ensuring that scripts are syntactically correct is a prerequisite for robust code that handles inputs correctly.

**Caveat:** This is a stretch; the rule is a syntax check, not a validation of external process control inputs.

### shellcheck:SC1028:rank_4:SR 3.5

- Source rule: `SC1028` — In [..] you have to escape \( \) or preferably combine [..] expressions.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.747172`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code portability and syntax

**Justification:** While SC1028 is primarily about syntax, the rationale mentions that some shells interpret syntax differently. This is tangentially related to the concept of ensuring inputs are not misinterpreted, but the rule itself is a static syntax check, not a security validation of external inputs.

**Caveat:** The rule is a linter warning for shell script portability, not a security-focused input validation mechanism.

### shellcheck:SC1033:rank_2:SR 3.5

- Source rule: `SC1033` — Test expression was opened with double [[ but closed with single ]. Make sure they match.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.959552`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies syntax errors in test expressions. While this is a form of code correctness, it is only tangentially related to the security objective of validating external inputs to prevent exploitation, though malformed syntax can lead to unexpected logic execution.

**Caveat:** This is a general code quality rule rather than a dedicated security input validation mechanism.

### shellcheck:SC1033:rank_6:SR 3.7

- Source rule: `SC1033` — Test expression was opened with double [[ but closed with single ]. Make sure they match.
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.697849`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** While the rule identifies an error condition, it is a static syntax error rather than a runtime error handling mechanism intended to prevent information disclosure during an attack.

**Caveat:** The rule is for development-time syntax correction, not runtime error handling.

### shellcheck:SC1034:rank_2:SR 3.5

- Source rule: `SC1034` — Test expression was opened with single [ but closed with double ]]. Make sure they match.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.990046`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule identifies a syntax error in a test expression, it is not related to validating external input content or syntax for security purposes. It is a static code quality check.

**Caveat:** The rule ensures the script itself is syntactically valid, which is a prerequisite for any logic, but it does not perform input validation as defined in SR 3.5.

### shellcheck:SC1035:rank_2:SR 3.5

- Source rule: `SC1035` — You need a space here
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.900271`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_input_validation`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is a basic syntax check, SR 3.5 requires validation of input syntax. However, the rule is a developer-time syntax check for shell scripts, not a runtime validation of industrial process control inputs.

**Caveat:** The rule is a static analysis check for script correctness, not a security-focused input validation mechanism for process control data.

### shellcheck:SC1036:rank_1:SR 3.5

- Source rule: `SC1036` — ( is invalid here. Did you forget to escape it?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_input_validation`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule identifies invalid syntax (misplaced parentheses) that could lead to unintended command execution. This aligns loosely with the intent of SR 3.5 to prevent content from being unintentionally interpreted as commands.

**Caveat:** The rule is a general-purpose static analysis check for shell scripts, not a specific security control for industrial process inputs.

### shellcheck:SC1037:rank_1:SR 3.5

- Source rule: `SC1037` — Braces are required for positionals over 9, e.g. ${10}.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and correct parameter expansion

**Justification:** While the rule is primarily about shell syntax, incorrect parameter expansion can lead to unintended behavior in scripts that process inputs, which relates to the broader goal of ensuring inputs are handled as intended.

**Caveat:** The rule is a static syntax check, not a security-focused input validation mechanism.

### shellcheck:SC1037:rank_3:SR 3.7

- Source rule: `SC1037` — Braces are required for positionals over 9, e.g. ${10}.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.824983`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and script robustness

**Justification:** Incorrect parameter expansion can cause scripts to fail or behave unexpectedly, which could be considered an error condition. However, the rule is a static syntax check rather than a runtime error handling strategy.

**Caveat:** The rule is a developer-time syntax check, not a runtime error handling mechanism.

### shellcheck:SC1038:rank_1:SR 3.5

- Source rule: `SC1038` — Shells are space sensitive. Use < <(cmd), not <<(cmd).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Syntactic correctness vs. Input validation`
- Directness: `Indirect`

**Security objective:** Code syntax correctness

**Justification:** While the rule is primarily about shell syntax, the use of incorrect redirection operators can lead to unexpected script behavior or failure to process inputs correctly. However, it does not directly address the security-focused input validation required by SR 3.5.

**Caveat:** The rule prevents script failure, which is a prerequisite for reliable input processing, but it is not a security validation mechanism.

### shellcheck:SC1039:rank_3:SR 3.5

- Source rule: `SC1039` — Remove indentation before end token (or use <<- and indent with tabs).
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.788214`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is a syntax fix, improper handling of here-documents or shell input can lead to command injection vulnerabilities, which relates to the broader goal of input validation.

**Caveat:** The rule is primarily a syntax correction rather than a security-focused input validation mechanism.

### shellcheck:SC1040:rank_1:SR 3.5

- Source rule: `SC1040` — When using <<-, you can only indent with tabs.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax/formatting issue, the rationale for SR 3.5 mentions that inputs should be pre-screened to prevent content from being misinterpreted. Incorrectly formatted here-documents can lead to unexpected script behavior, which is a form of input/command interpretation issue.

**Caveat:** The rule is primarily a linter check for code readability/correctness rather than a security-focused input validation mechanism.

### shellcheck:SC1046:rank_1:SR 3.5

- Source rule: `SC1046` — Couldn't find fi for this if.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_error_vs_input_validation`
- Directness: `indirect`

**Security objective:** Code correctness and input validation

**Justification:** While SC1046 is a static syntax error, ensuring code is syntactically correct is a prerequisite for robust input validation and preventing unexpected execution paths.

**Caveat:** The rule is a general linter check, not a security-specific input validation check.

### shellcheck:SC1051:rank_1:SR 3.5

- Source rule: `SC1051` — Semicolons directly after then are not allowed. Just remove it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While SC1051 enforces correct shell syntax, the rationale for SR 3.5 mentions that inputs passed to interpreters should be pre-screened to prevent unintended interpretation. However, SC1051 is a static syntax check, not a runtime input validation mechanism.

**Caveat:** The rule is a static syntax check, whereas the requirement focuses on runtime input validation.

### shellcheck:SC1055:rank_4:SR 3.7

- Source rule: `SC1055` — You need at least one command here. Use true; as a no-op.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.801526`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `code_quality_vs_error_handling`
- Directness: `indirect`

**Security objective:** Code robustness and error handling

**Justification:** While the rule is primarily a syntax check, ensuring that code blocks are not empty can be considered a basic form of robust error handling or defensive programming, which aligns loosely with the goal of identifying and handling error conditions.

**Caveat:** The rule is a static syntax requirement, not a functional error handling mechanism as described in SR 3.7.

### shellcheck:SC1056:rank_1:SR 3.5

- Source rule: `SC1056` — Expected a }. If you have one, try a ; or \n in front of it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_error_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation and syntax integrity

**Justification:** SC1056 identifies a syntax error where a closing brace is misinterpreted. While this is a static syntax issue, the rationale for SR 3.5 mentions that inputs passed to interpreters should be pre-screened to prevent content from being unintentionally interpreted as commands. A malformed script could potentially lead to unexpected execution paths if the input is dynamic.

**Caveat:** The rule is primarily a developer-time syntax check, whereas SR 3.5 focuses on runtime input validation.

### shellcheck:SC1056:rank_3:SR 3.7

- Source rule: `SC1056` — Expected a }. If you have one, try a ; or \n in front of it.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.831661`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntax_error_vs_error_handling`
- Directness: `indirect`

**Security objective:** Error handling and system robustness

**Justification:** SC1056 identifies a syntax error that would cause a script to fail. SR 3.7 requires handling error conditions without revealing exploitable information. While the rule helps prevent runtime crashes, it is a development-time check, not a runtime error handling mechanism.

**Caveat:** The rule prevents the error from occurring rather than handling it at runtime.

### shellcheck:SC1066:rank_2:SR 3.5

- Source rule: `SC1066` — Don't use $ on the left side of assignments.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.919762`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic_error_vs_input_validation`
- Directness: `indirect`

**Security objective:** Code correctness and syntax enforcement

**Justification:** While SC1066 is a syntax error, the rationale for SR 3.5 mentions that inputs passed to interpreters should be pre-screened to prevent content from being misinterpreted as commands. However, SC1066 is a static syntax error, not a runtime input validation issue.

**Caveat:** The relationship is extremely weak as the rule addresses developer syntax errors rather than runtime input validation of untrusted data.

### shellcheck:SC1067:rank_2:SR 3.5

- Source rule: `SC1067` — For indirection, use arrays, declare "var$n=value", or (for sh) read/eval
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.917838`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax, the use of 'eval' or dynamic variable construction (as mentioned in the rule's correct code) can lead to command injection vulnerabilities if inputs are not properly validated. However, the rule itself is a linter warning for syntax, not a security check for input validation.

**Caveat:** The rule suggests 'eval' as a solution, which is a common source of security vulnerabilities if not handled with extreme care.

### shellcheck:SC1070:rank_1:SR 3.5

- Source rule: `SC1070` — Parsing stopped here. Mismatched keywords or invalid parentheses?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic_to_functional`
- Directness: `indirect`

**Security objective:** Code integrity and robustness

**Justification:** While SC1070 identifies a syntax error, which could theoretically prevent a script from executing correctly, it is a general development quality rule rather than a specific input validation security control as required by SR 3.5.

**Caveat:** The rule is too generic to be considered a direct implementation of input validation.

### shellcheck:SC1074:rank_4:SR 3.7

- Source rule: `SC1074` — Did you forget the ;; after the previous case item?
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.836926`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and system stability

**Justification:** The rule addresses a syntax error that could lead to unexpected control flow or system failure. While not a direct security feature, robust code execution is a prerequisite for reliable error handling as required by SR 3.7.

**Caveat:** This is a general software quality rule, not a security-specific control.

### shellcheck:SC1074:rank_6:SR 3.3

- Source rule: `SC1074` — Did you forget the ;; after the previous case item?
- Rank: `6`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.800011`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Verification of system operation

**Justification:** Ensuring code is syntactically correct is a basic step in verifying that security functions operate as intended, but the rule itself is not a security verification mechanism.

**Caveat:** The rule is a general coding standard, not a security function verification tool.

### shellcheck:SC1075:rank_1:SR 3.5

- Source rule: `SC1075` — Use elif instead of else if.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `code_structure_vs_input_validation`
- Directness: `indirect`

**Security objective:** Code correctness and logic flow

**Justification:** While the rule is primarily about syntax, ensuring correct control flow in scripts that handle inputs can indirectly prevent logic errors that might bypass input validation checks. However, it is not a direct input validation mechanism.

**Caveat:** The rule is a linter warning for syntax, not a security-focused input validation check.

### shellcheck:SC1075:rank_2:SR 3.7

- Source rule: `SC1075` — Use elif instead of else if.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.832499`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `code_structure_vs_error_handling`
- Directness: `indirect`

**Security objective:** Code correctness and logic flow

**Justification:** Correcting control flow structures ensures that error conditions are evaluated as intended. If logic is flawed due to syntax misinterpretation, error handling might not trigger correctly, potentially leading to insecure states.

**Caveat:** The rule is a linter warning for syntax, not a security-focused error handling mechanism.

### shellcheck:SC1076:rank_1:SR 3.5

- Source rule: `SC1076` — Trying to do math? Use e.g. [ $((i/2+7)) -ge 18 ].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and correct syntax interpretation

**Justification:** The rule ensures correct arithmetic syntax in shell scripts, which prevents unintended interpretation of inputs. While this is a form of syntax validation, it is a general coding best practice rather than a specific security control for industrial process inputs.

**Caveat:** The rule is primarily a functional correctness check for shell scripts, not a security-focused input validation mechanism for IACS.

### shellcheck:SC1078:rank_1:SR 3.2 RE 1

- Source rule: `SC1078` — SC1078
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code integrity and syntax correctness

**Justification:** SC1078 identifies syntax errors (missing quotes). While syntax errors are not inherently malicious, ensuring code correctness is a prerequisite for robust security mechanisms, including those at entry/exit points.

**Caveat:** The rule is a general linter and not specifically targeted at security mechanisms.

### shellcheck:SC1080:rank_1:SR 3.5

- Source rule: `SC1080` — You need \ before line feeds to break lines in [ ].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** While SC1080 is a syntax correction for shell scripts, it ensures that the script is interpreted correctly. If the script processes inputs, ensuring correct syntax prevents unintended command execution, which aligns loosely with the goal of input validation.

**Caveat:** This is a general code quality rule, not a security-specific input validation rule.

### shellcheck:SC1082:rank_1:SR 3.5

- Source rule: `SC1082` — This file has a UTF-8 BOM. Remove it with: LC_CTYPE=C sed '1s/^...//' < yourscript.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** While the rule addresses a file encoding issue (BOM), it is technically a form of input validation for the shell interpreter. However, it is a functional requirement rather than a security-focused input validation requirement.

**Caveat:** The rule is primarily about functional execution, not security-critical input validation.

### shellcheck:SC1083:rank_1:SR 3.5

- Source rule: `SC1083` — This {/} is literal. Check if ; is missing or quote the expression.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** SC1083 warns about literal curly brackets which can indicate malformed syntax or unintended command execution. While this is a code quality issue, it relates to how the shell interprets input, which is tangentially relevant to SR 3.5's requirement to prevent unintended interpretation of inputs.

**Caveat:** The rule is primarily a linter warning for code correctness rather than a security-focused input validation mechanism.

### shellcheck:SC1087:rank_1:SR 3.5

- Source rule: `SC1087` — Use braces when expanding arrays, e.g. ${array[idx]} (or ${var}[.. to quiet).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and correct interpretation

**Justification:** While the rule is primarily a syntax fix, it ensures that variables are expanded as intended. In shell scripting, ambiguous syntax can lead to unintended command execution or logic errors, which relates tangentially to the requirement that inputs should not be misinterpreted by interpreters.

**Caveat:** The rule is primarily for code clarity rather than a security-focused input validation mechanism.

### shellcheck:SC1088:rank_1:SR 3.5

- Source rule: `SC1088` — Parsing stopped here. Invalid use of parentheses?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** While SC1088 is a static analysis rule for shell syntax, the rationale mentions that incorrect use of parentheses can lead to misinterpretation of commands. This relates to the broader concept of ensuring inputs are not misinterpreted, which is the core of SR 3.5.

**Caveat:** The rule is primarily a developer-experience/syntax check, not a security-focused input validation mechanism.

### shellcheck:SC1089:rank_1:SR 3.5

- Source rule: `SC1089` — Parsing stopped here. Is this keyword correctly matched up?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** SC1089 identifies structural syntax errors in shell scripts. If a script's structure is malformed, it may lead to unexpected execution paths, which is tangentially related to the requirement that inputs (or code logic) be validated to prevent unintended behavior.

**Caveat:** This is a general code quality rule, not a security-specific input validation rule.

### shellcheck:SC1090:rank_1:SR 3.2 RE 1

- Source rule: `SC1090` — Can't follow non-constant source. Use a directive to specify location
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** SC1090 warns about dynamic sourcing of files. If a path is controlled by an attacker, this could lead to arbitrary code execution. This relates to protecting entry points, though the rule is primarily about static analysis limitations.

**Caveat:** The rule is intended to help the static analyzer, not specifically to prevent malicious code injection, though the underlying risk is similar.

### shellcheck:SC1090:rank_3:SR 7.3

- Source rule: `SC1090` — Can't follow non-constant source. Use a directive to specify location
- Rank: `3`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.941283`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Configuration management and backup integrity

**Justification:** While SC1090 is a linter warning, ensuring that scripts correctly reference their dependencies is a minor aspect of maintaining system configuration and backup integrity, which is relevant to SR 7.3.

**Caveat:** The relationship is very weak; the rule is a development-time quality check, not a system-level backup requirement.

### shellcheck:SC1090:rank_6:SR 3.7

- Source rule: `SC1090` — Can't follow non-constant source. Use a directive to specify location
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.783265`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and system robustness

**Justification:** SC1090 helps prevent runtime errors caused by missing files. While this contributes to system stability, it is not directly related to the security-focused error handling requirements of SR 3.7.

**Caveat:** The rule is a general coding best practice rather than a security-specific error handling mechanism.

### shellcheck:SC1092:rank_6:SR 3.7

- Source rule: `SC1092` — Stopping at 100 source frames :O
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.858034`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** While SC1092 is a linter warning, it represents the system identifying an error condition (infinite recursion). However, it does not address the security-sensitive aspects of error handling (information disclosure) required by SR 3.7.

**Caveat:** The rule identifies an error, but does not manage the security implications of that error.

### shellcheck:SC1094:rank_1:SR 3.7

- Source rule: `SC1094` — Parsing of sourced file failed. Ignoring it.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and system robustness

**Justification:** SC1094 identifies a parsing error in a sourced file. While this is an error condition, it is a development-time static analysis finding rather than a runtime error handling mechanism as described in SR 3.7.

**Caveat:** The rule is a development tool, whereas the requirement applies to the control system's runtime behavior.

### shellcheck:SC1094:rank_6:SR 3.4

- Source rule: `SC1094` — Parsing of sourced file failed. Ignoring it.
- Rank: `6`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.804397`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software integrity

**Justification:** While SC1094 is a syntax error, failing to correctly parse a sourced file could lead to unexpected behavior or execution of incorrect code, which touches on the integrity of the software execution environment.

**Caveat:** The rule is primarily a linter warning, not a security integrity mechanism.

### shellcheck:SC1097:rank_1:SR 3.5

- Source rule: `SC1097` — Unexpected ==. For assignment, use =. For comparison, use [/[[.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_support`
- Directness: `low`

**Security objective:** Code correctness and logic integrity

**Justification:** While primarily a syntax/logic error, using incorrect operators in shell scripts can lead to unintended logic execution. If the script processes external inputs, this could theoretically lead to logic bypasses, though the rule itself is not a security control.

**Caveat:** The rule is a general coding best practice, not a security-specific input validation mechanism.

### shellcheck:SC1098:rank_1:SR 3.5

- Source rule: `SC1098` — Quote/escape special characters when using eval, e.g. eval "a=(b)".
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The use of 'eval' with unquoted variables is a classic command injection vector. Properly quoting inputs prevents the interpreter from executing unintended commands, which directly supports the requirement to validate input syntax and content.

**Caveat:** While the rule is a best practice for shell scripting, its application to 'industrial process control input' depends on whether the shell script is part of the control system's critical path.

### shellcheck:SC1098:rank_2:SR 3.7

- Source rule: `SC1098` — Quote/escape special characters when using eval, e.g. eval "a=(b)".
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.945378`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `indirect`

**Security objective:** Error handling and information disclosure

**Justification:** Improperly handled 'eval' statements can lead to crashes or unexpected behavior that might leak information in error messages, but the rule itself is primarily about code correctness rather than error handling strategy.

**Caveat:** The relationship is weak; the rule is not specifically designed to prevent information disclosure.

### shellcheck:SC1098:rank_3:SR 3.2 RE 1

- Source rule: `SC1098` — Quote/escape special characters when using eval, e.g. eval "a=(b)".
- Rank: `3`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.917928`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `mitigation`
- Directness: `indirect`

**Security objective:** Malicious code protection

**Justification:** By preventing command injection via 'eval', the rule reduces the attack surface for malicious code execution. However, it is a general coding practice rather than a dedicated malicious code protection mechanism.

**Caveat:** This is a preventative coding practice, not a security mechanism like an antivirus or firewall.

### shellcheck:SC1098:rank_8:SR 3.2

- Source rule: `SC1098` — Quote/escape special characters when using eval, e.g. eval "a=(b)".
- Rank: `8`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.74628`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code injection prevention

**Justification:** The rule prevents improper shell evaluation which could be exploited to execute malicious code, aligning loosely with the prevention of malicious code execution.

**Caveat:** The rule is primarily a coding best practice for shell stability rather than a dedicated security mechanism against malicious code.

### shellcheck:SC1100:rank_3:SR 3.5

- Source rule: `SC1100` — This is a Unicode dash. Delete and retype as ASCII minus.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.904519`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** While SC1100 is a syntax fix, SR 3.5 requires validating the syntax of inputs. Ensuring that scripts use correct ASCII characters can be considered a very low-level form of syntax validation, though the rule itself is primarily about code correctness rather than security-critical input validation.

**Caveat:** The rule is a general code quality check, not a security-focused input validation mechanism.

### shellcheck:SC1101:rank_1:SR 3.5

- Source rule: `SC1101` — Delete trailing spaces after \ to break line (or use quotes for literal space).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule identifies a syntax error where trailing spaces cause command misinterpretation. While this is a code quality issue, it relates to how the shell interprets input, which is tangentially related to the broader concept of ensuring inputs are interpreted as intended.

**Caveat:** This is a stretch; the rule is primarily about shell syntax correctness rather than security-critical input validation.

### shellcheck:SC1102:rank_1:SR 3.5

- Source rule: `SC1102` — Shells disambiguate $(( differently or not at all. For $(command substitution), add space after $( . For $((arithmetics)), fix parsing errors.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule addresses ambiguous shell syntax that can lead to unintended command execution or parsing errors. While this is a form of input/syntax validation, it is primarily a code quality/correctness issue rather than a security-focused input validation against malicious data as described in SR 3.5.

**Caveat:** The rule prevents potential misinterpretation of commands, which is a prerequisite for secure execution, but it does not address the validation of external data inputs.

### shellcheck:SC1103:rank_4:SR 7.7

- Source rule: `SC1103` — This shell type is unknown. Use e.g. sh or bash.
- Rank: `4`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.742885`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Configuration Management`
- Directness: `Indirect`

**Security objective:** Least functionality

**Justification:** The rule ensures that the shell environment is correctly identified and configured, which is a prerequisite for enforcing least functionality by ensuring only supported and intended shell environments are used.

**Caveat:** This is a static analysis rule for code quality/configuration, not a direct control for prohibiting system-level functions or services.

### shellcheck:SC1103:rank_8:SR 3.3

- Source rule: `SC1103` — This shell type is unknown. Use e.g. sh or bash.
- Rank: `8`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.691069`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Verification`
- Directness: `Indirect`

**Security objective:** Security functionality verification

**Justification:** Ensuring that scripts run in the intended shell environment is a minor aspect of verifying the intended operation of security-related scripts or automation.

**Caveat:** The rule is a development-time check, whereas SR 3.3 focuses on operational verification of security functions.

### shellcheck:SC1105:rank_1:SR 3.5

- Source rule: `SC1105` — Shells disambiguate (( differently or not at all. If the first ( should start a subshell, add a space after it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax disambiguation

**Justification:** SC1105 addresses shell syntax ambiguity. While the SR 3.5 rationale mentions that inputs passed to interpreters should be pre-screened to prevent unintended interpretation, this rule is a general syntax warning rather than a security-focused input validation mechanism.

**Caveat:** The rule is a general coding best practice rather than a security control.

### shellcheck:SC1106:rank_1:SR 3.5

- Source rule: `SC1106` — In arithmetic contexts, use < instead of -lt
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule enforces correct syntax in arithmetic contexts, preventing unintended interpretation of flags as variables. This aligns with the requirement to validate syntax of inputs to prevent unintended command interpretation.

**Caveat:** While the rule is a static analysis check for syntax, it directly supports the objective of ensuring inputs are interpreted as intended.

### shellcheck:SC1106:rank_3:SR 3.7

- Source rule: `SC1106` — In arithmetic contexts, use < instead of -lt
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.68608`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error handling`
- Directness: `indirect`

**Security objective:** Error handling and remediation

**Justification:** The rule identifies a potential logic error in shell scripts. While it improves code quality, it is not specifically related to the security requirement of handling error conditions without leaking sensitive information.

**Caveat:** The relationship is weak as the rule is a general syntax check rather than a security-focused error handling mechanism.

### shellcheck:SC1107:rank_1:SR 3.7

- Source rule: `SC1107` — This directive is unknown. It will be ignored.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error handling`
- Directness: `indirect`

**Security objective:** Error handling and remediation

**Justification:** The rule warns about unrecognized directives, which is a form of error handling during script parsing. However, it does not directly address the security-sensitive error handling required by SR 3.7.

**Caveat:** The rule is a development-time diagnostic, not a runtime security control.

### shellcheck:SC1108:rank_1:SR 3.5

- Source rule: `SC1108` — You need a space before and after the = .
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Syntax validation of shell script expressions

**Justification:** While SC1108 enforces correct syntax for shell operators, which is a form of input validation, it is a general coding quality rule rather than a security-focused input validation mechanism for industrial process control inputs as defined by SR 3.5.

**Caveat:** The rule helps prevent logic errors that could lead to unexpected behavior, but it is not a security control for external inputs.

### shellcheck:SC1109:rank_4:SR 3.5

- Source rule: `SC1109` — This is an unquoted HTML entity. Replace with corresponding character.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.74136`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** While the rule is primarily about fixing copy-paste errors, unquoted or malformed characters can lead to command injection or misinterpretation if they appear in inputs processed by the system.

**Caveat:** The rule is a general code quality check, not a security-specific input validation mechanism.

### shellcheck:SC1110:rank_1:SR 3.5

- Source rule: `SC1110` — This is a Unicode quote. Delete and retype it (or quote to make literal).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** Unicode quotes can cause unexpected behavior or errors when scripts process inputs. Ensuring standard ASCII quotes is a form of syntax validation that prevents misinterpretation of commands.

**Caveat:** This is a code quality rule; it does not perform security-focused input validation as defined by IEC 62443-3-3.

### shellcheck:SC1111:rank_1:SR 3.5

- Source rule: `SC1111` — This is a Unicode quote. Delete and retype it (or ignore/singlequote for literal).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_support`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about fixing syntax errors, ensuring that input is correctly parsed and interpreted is a foundational aspect of input validation to prevent unexpected behavior.

**Caveat:** The rule is a linter check for typos, not a security-focused input validation mechanism.

### shellcheck:SC1112:rank_1:SR 3.5

- Source rule: `SC1112` — This is a Unicode quote. Delete and retype it (or ignore/doublequote for literal).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_support`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** Ensuring that input is correctly parsed and interpreted is a foundational aspect of input validation to prevent unexpected behavior, even if the rule is primarily a linter check.

**Caveat:** The rule is a linter check for typos, not a security-focused input validation mechanism.

### shellcheck:SC1114:rank_1:SR 3.5

- Source rule: `SC1114` — Remove leading spaces before the shebang.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Ensuring correct script execution environment

**Justification:** While the rule ensures the OS correctly identifies the script interpreter, it is a low-level file format requirement rather than an input validation requirement for industrial process control data.

**Caveat:** The rule prevents the OS from misinterpreting the file type, which is a form of system-level input validation, but it is not the type of application-level input validation intended by SR 3.5.

### shellcheck:SC1116:rank_1:SR 3.5

- Source rule: `SC1116` — Missing $ on a $((..)) expression? (or use ( ( for arrays).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntactic_correctness`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax correction for shell arithmetic, ensuring correct syntax in scripts prevents unintended behavior or logic errors that could potentially be exploited if the script processes external inputs.

**Caveat:** The rule is a general coding best practice rather than a specific security-focused input validation check.

### shellcheck:SC1117:rank_2:SR 3.5

- Source rule: `SC1117` — Backslash is literal in "\n". Prefer explicit escaping: "\\n".
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.964753`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily stylistic, improper string handling and escaping can lead to injection vulnerabilities. However, this specific rule is about literal backslashes, which is generally not a security-critical input validation issue.

**Caveat:** The rule itself is explicitly labeled as stylistic and retired in newer versions of ShellCheck.

### shellcheck:SC1125:rank_1:SR 3.5

- Source rule: `SC1125` — Invalid key=value pair in directive
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic`
- Directness: `indirect`

**Security objective:** Input validation and configuration parsing

**Justification:** While the rule is about parsing ShellCheck directives, it touches on the general principle of validating input syntax to prevent misinterpretation, which is a core concept of SR 3.5.

**Caveat:** The rule is specific to static analysis tool configuration, not industrial process control inputs.

### shellcheck:SC1128:rank_5:SR 3.2 RE 1

- Source rule: `SC1128` — The shebang must be on the first line. Delete blanks and move comments.
- Rank: `5`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.745756`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code execution integrity

**Justification:** Ensuring the correct interpreter is used prevents unexpected execution behavior, which is a minor aspect of ensuring code runs as intended, but it does not constitute a malicious code protection mechanism.

**Caveat:** The rule is a best practice for script execution, not a security control for malicious code.

### shellcheck:SC1128:rank_7:SR 2.4 RE 1

- Source rule: `SC1128` — The shebang must be on the first line. Delete blanks and move comments.
- Rank: `7`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.686558`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code execution integrity

**Justification:** The rule ensures the script is interpreted correctly, which is a prerequisite for reliable execution, but it does not perform an integrity check (e.g., cryptographic verification) as required by SR 2.4.

**Caveat:** The rule is a syntax/configuration check, not an integrity verification mechanism.

### shellcheck:SC1130:rank_8:SR 3.5

- Source rule: `SC1130` — You need a space before the :.
- Rank: `8`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.786821`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax, it involves the shell interpreter. Input validation (SR 3.5) aims to prevent malformed input from being interpreted as commands. However, this specific rule is a static syntax check, not a runtime input validation mechanism.

**Caveat:** The rule is a static analysis check for developer error, not a runtime security control for input validation.

### shellcheck:SC1132:rank_5:SR 3.5

- Source rule: `SC1132` — This & terminates the command. Escape it or add space after & to silence.
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.84524`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell syntax, improper handling of special characters in inputs (like URLs) can lead to command injection or unexpected behavior, which relates to the broader goal of validating input content.

**Caveat:** The rule is a static syntax check for shell scripts, not a comprehensive input validation mechanism for industrial control inputs.

### shellcheck:SC1135:rank_1:SR 3.5

- Source rule: `SC1135` — Prefer escape over ending quote to make $ literal. Instead of "It costs $"5, use "It costs \$5"
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule encourages cleaner syntax to avoid unintended interpretation of shell variables. While this improves code maintainability and reduces the risk of injection-style errors (e.g., eval misuse), it is primarily a stylistic/best-practice rule rather than a direct input validation mechanism.

**Caveat:** The rule is primarily stylistic; however, it touches upon the safe handling of inputs passed to interpreters, which is relevant to SR 3.5.

### shellcheck:SC1136:rank_1:SR 3.5

- Source rule: `SC1136` — Unexpected characters after terminating ]. Missing semicolon/linefeed?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies syntax errors in shell scripts that could lead to unexpected execution paths. While this is a form of code correctness, it is only tangentially related to the security objective of validating external inputs to prevent injection or malicious control.

**Caveat:** The rule is primarily a linter for syntax errors rather than a security-focused input validation mechanism.

### shellcheck:SC1137:rank_6:SR 3.5

- Source rule: `SC1137` — Missing second ( to start arithmetic for ((;;)) loop
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.832478`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** While the rule is a basic syntax check, ensuring correct syntax in scripts is a foundational step in preventing malformed inputs or unexpected execution paths, which aligns loosely with the goal of input validation.

**Caveat:** The rule is a static syntax check, not a security-focused input validation mechanism.

### shellcheck:SC1139:rank_2:SR 3.5

- Source rule: `SC1139` — Use || instead of -o between test commands.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.897101`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax fix, ensuring correct logical operators in conditional statements can prevent logic errors that might lead to improper input handling or bypasses in security-sensitive scripts.

**Caveat:** The rule is a general syntax correction, not a specific input validation mechanism.

### shellcheck:SC1140:rank_1:SR 3.5

- Source rule: `SC1140` — Unexpected parameters after condition. Missing &&/||, or bad expression?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic_to_functional`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule identifies malformed shell syntax, it is a stretch to classify this as 'input validation' in the context of IEC 62443-3-3, which focuses on validating process control inputs to prevent exploitation.

**Caveat:** The rule is a static analysis check for code syntax, not a runtime validation of external inputs.

### shellcheck:SC1141:rank_6:SR 3.7

- Source rule: `SC1141` — Unexpected tokens after compound command. Bad redirection or missing ;/&&/||/|?
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.768572`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntactic_error_vs_error_handling`
- Directness: `indirect`

**Security objective:** Robust error handling and code quality

**Justification:** While SC1141 is a syntax check, it relates to how a script handles command execution flow. SR 3.7 concerns error handling. While the rule is not a security control, fixing syntax errors is a prerequisite for robust error handling in scripts.

**Caveat:** The rule is a developer-level syntax check, whereas the requirement is a system-level security design requirement.

### shellcheck:SC1141:rank_7:SR 3.5

- Source rule: `SC1141` — Unexpected tokens after compound command. Bad redirection or missing ;/&&/||/|?
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.728178`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule identifies a syntax error in shell script redirection. While the SR 3.5 focuses on validating input content to prevent injection or malformed data, this rule is a basic syntax check for script execution. It is not a security-specific input validation mechanism.

**Caveat:** The rule is a general code quality/syntax check, not a security-focused input validation control.

### shellcheck:SC1144:rank_4:SR 3.2 RE 1

- Source rule: `SC1144` — external-sources can only be enabled in .shellcheckrc, not in individual files.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.79694`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Sandboxing/Isolation`
- Directness: `Indirect`

**Security objective:** Malicious code protection

**Justification:** The rule enforces a sandbox configuration to prevent arbitrary file access. While this is a form of isolation, it is a development-time tool configuration rather than a runtime malicious code protection mechanism for the control system.

**Caveat:** The rule is about static analysis tool configuration, not the runtime security of the control system itself.

### shellcheck:SC1144:rank_7:SR 3.2

- Source rule: `SC1144` — external-sources can only be enabled in .shellcheckrc, not in individual files.
- Rank: `7`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.747618`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Sandboxing/Isolation`
- Directness: `Indirect`

**Security objective:** Malicious code protection

**Justification:** The rule uses a sandbox concept to limit file access. While sandboxing is mentioned in the SR 3.2 rationale as a prevention technique, this rule applies to the static analysis tool, not the control system component.

**Caveat:** The rule is a development-time constraint, not a runtime control system security mechanism.

### shellcheck:SC1145:rank_3:SR 3.7

- Source rule: `SC1145` — Unknown external-sources value. Expected true/false.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.896821`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Configuration validation

**Justification:** While the rule is about configuration validation, it is a stretch to map it to SR 3.7 (Error handling). However, both involve ensuring that system configurations or error states are handled in a predictable, non-exploitable manner.

**Caveat:** The relationship is purely structural/procedural rather than functional.

### shellcheck:SC2001:rank_1:SR 3.5

- Source rule: `SC2001` — See if you can use ${variable//search/replace} instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule encourages using shell parameter expansion instead of external tools like sed. While this improves efficiency and reduces reliance on external interpreters (which can be a vector for injection), it is not a direct implementation of input validation as defined in SR 3.5.

**Caveat:** The rule is a best practice for code quality, not a security control for input validation.

### shellcheck:SC2002:rank_1:SR 3.5

- Source rule: `SC2002` — SC2002
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about code efficiency (avoiding UUOC), using direct file redirection instead of pipes can sometimes prevent issues related to shell command injection or unexpected behavior in complex pipelines, which relates to input handling.

**Caveat:** The primary intent of the rule is performance, not security.

### shellcheck:SC2004:rank_2:SR 3.5

- Source rule: `SC2004` — SC2004
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.905459`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and safe interpretation

**Justification:** The rule prevents unintended shell expansion in arithmetic contexts, which is a form of input sanitization. While it is a coding best practice, it aligns with the goal of preventing malformed inputs from being interpreted as commands.

**Caveat:** This is a language-specific coding convention rather than a comprehensive input validation framework.

### shellcheck:SC2005:rank_1:SR 3.5

- Source rule: `SC2005` — SC2005
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code quality and input handling

**Justification:** SC2005 warns against unnecessary command substitution which can lead to unexpected behavior or loss of exit codes. While this is a code quality issue, it is not directly related to validating the syntax or content of industrial process control inputs as required by SR 3.5.

**Caveat:** The rule improves code robustness, which is a prerequisite for secure input handling, but it does not perform input validation itself.

### shellcheck:SC2006:rank_10:SR 3.5

- Source rule: `SC2006` — SC2006
- Rank: `10`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.723428`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is primarily about syntax, backtick command substitution can lead to unexpected command execution if variables are not properly quoted, which relates to the broader goal of preventing unintended command interpretation.

**Caveat:** The rule is primarily a code style/modernization rule rather than a direct security input validation control.

### shellcheck:SC2007:rank_1:SR 3.5

- Source rule: `SC2007` — Use $((..)) instead of deprecated $[..].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule enforces the use of standard arithmetic syntax. While primarily for modernization, ensuring correct syntax for arithmetic operations can prevent logic errors that might be exploited in inputs.

**Caveat:** This is a minor syntax improvement and does not constitute a robust input validation mechanism.

### shellcheck:SC2008:rank_1:SR 3.5

- Source rule: `SC2008` — echo doesn't read from stdin, are you sure you should be piping to it?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code quality and input handling

**Justification:** While the rule identifies a logic error (piping to a command that ignores input), it is not a security-focused input validation check. However, it relates to the broader goal of ensuring that data flow and command execution behave as intended, which is a prerequisite for secure input handling.

**Caveat:** The rule is primarily a code quality/usability check rather than a security-critical input validation mechanism.

### shellcheck:SC2009:rank_1:SR 3.7

- Source rule: `SC2009` — Consider using pgrep instead of grepping ps output.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust process management

**Justification:** The rule improves the robustness of process identification. While not directly related to error handling or information disclosure, more robust code is less likely to produce unexpected error states or ambiguous results that could complicate incident response or troubleshooting.

**Caveat:** The relationship to error handling is weak; the rule is primarily about code efficiency and correctness.

### shellcheck:SC2009:rank_10:SR 1.2

- Source rule: `SC2009` — Consider using pgrep instead of grepping ps output.
- Rank: `10`
- IEC target: `SR 1.2` — Software process and device identification and authentication
- Relative score: `0.704042`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Process identification

**Justification:** The rule improves the accuracy of process identification in scripts, which is a prerequisite for managing software processes, but it does not implement authentication or identification mechanisms as required by SR 1.2.

**Caveat:** The rule is a coding best practice, not a security control for authentication.

### shellcheck:SC2013:rank_1:SR 3.5

- Source rule: `SC2013` — To read lines rather than words, pipe/redirect to a while read loop.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule encourages safer file reading practices to avoid unintended globbing or word splitting, which is a form of input handling. While not direct input validation of control system parameters, it aligns with the principle of handling data safely to prevent unintended interpretation.

**Caveat:** The rule is a general coding best practice rather than a security-specific input validation control.

### shellcheck:SC2013:rank_8:SR 3.7

- Source rule: `SC2013` — To read lines rather than words, pipe/redirect to a while read loop.
- Rank: `8`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.686408`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and secure coding

**Justification:** While the rule is primarily about syntax, improper handling of file input in shell scripts can lead to unexpected behavior or errors. SR 3.7 requires error handling that does not leak information. The connection is very weak as the rule is about functional correctness rather than security-sensitive error handling.

**Caveat:** The rule is a best practice for script robustness, which is a prerequisite for secure system operation, but it does not directly address the security-specific requirements of SR 3.7.

### shellcheck:SC2015:rank_3:SR 5.2 RE 3

- Source rule: `SC2015` — SC2015
- Rank: `3`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `0.823354`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect support`
- Directness: `Low`

**Security objective:** Robust error handling and fail-safe logic

**Justification:** The rule prevents unintended execution of commands due to logical errors in shell scripts. While not specifically about network boundary protection, it promotes the 'fail-safe' principle by ensuring that conditional logic behaves as intended, preventing accidental execution of destructive commands.

**Caveat:** The rule is a general coding practice for shell scripts and is not specific to network boundary protection mechanisms.

### shellcheck:SC2016:rank_1:SR 3.5

- Source rule: `SC2016` — SC2016
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is primarily about shell syntax (quoting), improper quoting can lead to unintended variable expansion, which is a prerequisite for certain types of command injection or input validation bypasses.

**Caveat:** The rule is a general coding best practice and not a direct security control for input validation.

### shellcheck:SC2017:rank_4:SR 3.5

- Source rule: `SC2017` — Increase precision by replacing a/bc with ac/b.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.713958`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and data integrity

**Justification:** The rule addresses arithmetic precision, which is a form of data integrity. While not a direct security validation of external inputs, ensuring correct calculation logic is a best practice for robust software that processes control inputs.

**Caveat:** This is a quality/correctness issue rather than a security-focused input validation requirement.

### shellcheck:SC2018:rank_1:SR 3.5

- Source rule: `SC2018` — Use [:lower:] to support accents and foreign alphabets.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** Using character classes instead of ranges is a best practice for handling internationalized input correctly. This relates to input validation by ensuring that the system correctly interprets and processes diverse character sets, preventing unexpected behavior.

**Caveat:** The rule is primarily about internationalization/correctness rather than security-critical input validation, though it prevents logic errors that could arise from malformed string processing.

### shellcheck:SC2018:rank_10:SR 1.7

- Source rule: `SC2018` — Use [:lower:] to support accents and foreign alphabets.
- Rank: `10`
- IEC target: `SR 1.7` — Strength of password-based authentication
- Relative score: `0.694997`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct character set handling in shell scripts

**Justification:** While the rule is about string processing, the mention of 'character types' in SR 1.7 could be loosely associated with character set handling, though the rule does not specifically address password strength or authentication.

**Caveat:** The association is purely lexical based on the concept of character sets.

### shellcheck:SC2019:rank_1:SR 1.7

- Source rule: `SC2019` — Use [:upper:] to support accents and foreign alphabets.
- Rank: `1`
- IEC target: `SR 1.7` — Strength of password-based authentication
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct character set handling in shell scripts

**Justification:** Similar to SC2018, this rule addresses character set support. SR 1.7 requires support for a variety of character types in passwords. The rule is not about password security, but the concepts of character sets overlap.

**Caveat:** The association is purely lexical based on the concept of character sets.

### shellcheck:SC2019:rank_2:SR 3.5

- Source rule: `SC2019` — Use [:upper:] to support accents and foreign alphabets.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.933751`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Input validation and character encoding consistency

**Justification:** The rule encourages using POSIX character classes for portability and correctness, which can prevent unexpected behavior in scripts. While not a direct security control, consistent character handling is a prerequisite for robust input validation.

**Caveat:** The rule is primarily a best practice for portability rather than a security-focused input validation mechanism.

### shellcheck:SC2020:rank_1:SR 3.5

- Source rule: `SC2020` — tr replaces sets of chars, not words (mentioned due to duplicates).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and data integrity

**Justification:** The rule identifies a logic error in string processing that could lead to malformed data being processed by the system. While it is a general programming best practice, it relates to the requirement of ensuring input content is correctly interpreted and validated.

**Caveat:** The rule is primarily a functional correctness issue rather than a direct security validation check, but incorrect string processing can lead to security vulnerabilities if the output is used in sensitive contexts.

### shellcheck:SC2021:rank_1:SR 3.5

- Source rule: `SC2021` — Don't use [] around ranges in tr, it replaces literal square brackets.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `3/5`
- Relation type: `input validation`
- Directness: `indirect`

**Security objective:** Input validation and sanitization

**Justification:** The rule ensures that character ranges are correctly specified in input processing tools, preventing unintended behavior that could lead to improper input handling.

**Caveat:** The rule is primarily a functional correctness issue, but it relates to the broader category of ensuring input processing logic behaves as intended.

### shellcheck:SC2021:rank_3:SR 3.7

- Source rule: `SC2021` — Don't use [] around ranges in tr, it replaces literal square brackets.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.944736`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error handling`
- Directness: `indirect`

**Security objective:** Robust input processing

**Justification:** While the rule is about syntax, incorrect syntax in input processing can lead to unexpected errors or failures that might be relevant to error handling.

**Caveat:** The relationship is weak as the rule is a static syntax correction rather than an error handling mechanism.

### shellcheck:SC2021:rank_4:SR 3.2 RE 1

- Source rule: `SC2021` — Don't use [] around ranges in tr, it replaces literal square brackets.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.939161`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `malicious code protection`
- Directness: `indirect`

**Security objective:** Input sanitization

**Justification:** Ensuring that input processing tools like 'tr' are used correctly is a prerequisite for effective input filtering, which is a component of malicious code protection.

**Caveat:** The rule is a general coding best practice and not a specific malicious code protection mechanism.

### shellcheck:SC2022:rank_5:SR 3.5

- Source rule: `SC2022` — Note that unlike globs, o* here matches ooo but not oscar.
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.760054`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Ensure correct interpretation of input data

**Justification:** The rule identifies a common mistake in regex usage that could lead to unintended input matching. While this is a coding error, it relates to the broader concept of ensuring inputs are processed as intended, which is a component of input validation.

**Caveat:** The rule is primarily a functional correctness check rather than a security-focused input validation check.

### shellcheck:SC2024:rank_2:SR 7.3

- Source rule: `SC2024` — sudo doesn't affect redirects. Use ..| sudo tee file
- Rank: `2`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.890525`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Privilege management for system operations

**Justification:** The rule ensures commands run with correct privileges, which is relevant to performing system backups (SR 7.3) correctly, but the rule itself is not specific to backup operations.

**Caveat:** The rule is a general shell best practice, not a specific control for backup integrity.

### shellcheck:SC2024:rank_4:SR 3.2 RE 1

- Source rule: `SC2024` — sudo doesn't affect redirects. Use ..| sudo tee file
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.79258`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Privilege management and file access control

**Justification:** The rule prevents unintended file access by ensuring commands run with the correct privileges. While this is a security best practice, it is not a direct implementation of malicious code protection at entry/exit points as defined in SR 3.2.

**Caveat:** Could be argued as a minor component of system hardening, but not a primary control for malicious code protection.

### shellcheck:SC2024:rank_8:SR 3.4

- Source rule: `SC2024` — sudo doesn't affect redirects. Use ..| sudo tee file
- Rank: `8`
- IEC target: `SR 3.4` — Software and information integrity
- Relative score: `0.752703`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Direct support`
- Directness: `Direct`

**Security objective:** Integrity of information at rest

**Justification:** The rule prevents privilege escalation or incorrect permission usage during file redirection, which is a mechanism to protect the integrity of system files from unauthorized modification by users lacking appropriate permissions.

**Caveat:** The rule is primarily about correct shell usage, but it directly impacts the ability to enforce file system permissions, which is a core component of protecting information at rest.

### shellcheck:SC2026:rank_2:SR 3.2 RE 1

- Source rule: `SC2026` — This word is outside of quotes. Did you intend to 'nest '"'single quotes'"' instead?
- Rank: `2`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.9514`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code correctness and injection prevention

**Justification:** The rule prevents shell command misinterpretation, which could theoretically be exploited to bypass security controls, but it is primarily a syntax/logic error check rather than a malicious code protection mechanism.

**Caveat:** The rule is a general coding best practice and not specifically designed for security-critical malicious code protection.

### shellcheck:SC2026:rank_10:SR 3.5

- Source rule: `SC2026` — This word is outside of quotes. Did you intend to 'nest '"'single quotes'"' instead?
- Rank: `10`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.819293`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_error_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation and command injection prevention

**Justification:** While SC2026 is primarily a syntax error, improper quoting in shell scripts can lead to command injection vulnerabilities if user-controlled input is involved. SR 3.5 requires input validation to prevent such issues. The rule helps ensure the script behaves as intended, which is a prerequisite for secure input handling.

**Caveat:** The rule is a general syntax check, not a security-specific input validation check.

### shellcheck:SC2028:rank_7:SR 3.5

- Source rule: `SC2028` — echo won't expand escape sequences. Consider printf.
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.819068`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** While SC2028 is primarily about formatting, the rationale mentions that printf should be used to avoid unintended interpretation of escape sequences. This aligns loosely with the principle of preventing unintended command interpretation mentioned in the SR 3.5 rationale.

**Caveat:** The rule is primarily a coding best practice for output formatting rather than a security-critical input validation mechanism.

### shellcheck:SC2030:rank_1:SR 3.3

- Source rule: `SC2030` — SC2030
- Rank: `1`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Security functionality verification

**Justification:** While SC2030 is a generic placeholder for a ShellCheck rule, static analysis rules in general support the verification of security functions as required by SR 3.3. However, without the specific rule definition, the link is purely speculative.

**Caveat:** The rule SC2030 is not fully defined in the provided context.

### shellcheck:SC2031:rank_2:SR 3.7

- Source rule: `SC2031` — SC2031
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.991149`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and state consistency

**Justification:** The rule addresses a logic error where variables are not updated as expected due to subshell behavior. While this is a functional bug, it can lead to incorrect state management, which is relevant to error handling and system reliability, though it is not a direct security control.

**Caveat:** This is primarily a functional correctness issue rather than a security-specific error handling mechanism.

### shellcheck:SC2035:rank_7:SR 3.7

- Source rule: `SC2035` — Use ./glob or -- glob so names with dashes won't become options.
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.683789`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and robust operation

**Justification:** While the rule prevents unexpected behavior (which could be considered an error condition), it is primarily a coding best practice for shell scripts rather than a system-level error handling mechanism as defined in SR 3.7.

**Caveat:** The rule prevents silent failures, which aligns loosely with the goal of identifying error conditions.

### shellcheck:SC2038:rank_2:SR 3.7

- Source rule: `SC2038` — Use -print0/-0 or find -exec + to allow for non-alphanumeric filenames.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.758923`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness and error handling

**Justification:** The rule improves robustness by preventing unexpected behavior when processing filenames. While not directly an error handling requirement, it prevents a class of errors that could lead to system instability or unexpected execution paths.

**Caveat:** The rule is primarily about input sanitization/robustness rather than the specific error handling/reporting requirements of SR 3.7.

### shellcheck:SC2039:rank_9:SR 3.5

- Source rule: `SC2039` — In POSIX sh, something is undefined.
- Rank: `9`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.701272`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and secure coding

**Justification:** While SC2039 is primarily about portability, using non-standard shell features can sometimes lead to unexpected behavior in different environments, which is tangentially related to the robustness of scripts handling inputs.

**Caveat:** The rule is not specifically designed for security or input validation.

### shellcheck:SC2041:rank_1:SR 3.5

- Source rule: `SC2041` — This is a literal string. To run as a command, use $(..) instead of '..' .
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command execution safety

**Justification:** The rule prevents accidental string literal usage where command execution was intended. While this is a coding best practice, it relates to SR 3.5 because improper handling of inputs or command strings can lead to unintended execution, which is a form of input validation failure.

**Caveat:** The rule is primarily a functional correctness check rather than a security-focused input validation check, though it prevents unintended command execution.

### shellcheck:SC2042:rank_1:SR 3.5

- Source rule: `SC2042` — Use spaces, not commas, to separate loop elements.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies a syntax error in a loop that could lead to unexpected behavior if the input is misinterpreted. While this is a form of syntax validation, it is primarily a code quality issue rather than a security-focused input validation against malicious data.

**Caveat:** The rule is a general code quality check; its security relevance is limited to preventing logic errors that might arise from malformed input structures.

### shellcheck:SC2043:rank_2:SR 3.5

- Source rule: `SC2043` — This loop will only ever run once for a constant value. Did you perhaps mean to loop over dir/*, $var or $(cmd)?
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.99872`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies a potential logic error in how data is processed. If the loop is intended to process multiple inputs but only processes one, it could lead to incomplete input processing, which is a minor aspect of input validation.

**Caveat:** This is primarily a code quality/logic check, not a security-focused input validation check.

### shellcheck:SC2044:rank_1:SR 2.11

- Source rule: `SC2044` — For loops over find output are fragile. Use find -exec or a while read loop.
- Rank: `1`
- IEC target: `SR 2.11` — Timestamps
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and reliability of file processing

**Justification:** While the rule improves code robustness by preventing errors in file handling, it is not directly related to the generation of timestamps for audit records. It is only tangentially relevant if the file processing involves audit logs.

**Caveat:** The rule is a general coding best practice and does not specifically target audit record generation or timestamping.

### shellcheck:SC2044:rank_2:SR 2.9 RE 1

- Source rule: `SC2044` — For loops over find output are fragile. Use find -exec or a while read loop.
- Rank: `2`
- IEC target: `SR 2.9 RE 1` — Warn when audit record storage capacity threshold reached
- Relative score: `0.905071`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and reliability of file processing

**Justification:** The rule improves code robustness, which could indirectly help ensure that audit log processing scripts do not fail. However, it does not directly address the requirement for warning about audit storage capacity.

**Caveat:** The rule is a general coding best practice and does not specifically target audit storage management.

### shellcheck:SC2045:rank_5:SR 3.5

- Source rule: `SC2045` — Iterating over ls output is fragile. Use globs.
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.91757`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and sanitization

**Justification:** While the rule is primarily about shell script robustness, it touches on the concept of 'parsing' and 'interpreting' inputs (filenames). SR 3.5 requires validating inputs to prevent unintended interpretation. However, the rule is a coding style recommendation rather than a security-critical input validation mechanism.

**Caveat:** The rule is a best practice for script reliability, not a security control for industrial process inputs.

### shellcheck:SC2046:rank_4:SR 3.5

- Source rule: `SC2046` — Quote this to prevent word splitting.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.907663`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** Unquoted command substitution allows for word splitting and globbing, which can be exploited to inject unintended arguments or commands, directly violating the principle of validating input content.

**Caveat:** While SC2046 is a coding best practice, it serves as a fundamental defense against command injection, which is a core concern of SR 3.5.

### shellcheck:SC2048:rank_1:SR 3.5

- Source rule: `SC2048` — Use "$@" (with quotes) to prevent whitespace problems.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** Unquoted shell variables are a common source of command injection and unintended interpretation of input. SR 3.5 explicitly requires that inputs passed to interpreters be pre-screened to prevent content from being misinterpreted as commands.

**Caveat:** While the rule is a best practice, it is a specific implementation detail of the broader requirement for input validation.

### shellcheck:SC2048:rank_4:SR 3.2 RE 1

- Source rule: `SC2048` — Use "$@" (with quotes) to prevent whitespace problems.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.7775`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and malicious code prevention

**Justification:** Improperly quoted variables can lead to command injection or unexpected execution paths if inputs are malicious. While the rule is primarily about correctness, it has a secondary security benefit in preventing injection-style vulnerabilities at entry points.

**Caveat:** The rule is primarily a functional correctness issue rather than a dedicated security mechanism.

### shellcheck:SC2048:rank_7:SR 3.7

- Source rule: `SC2048` — Use "$@" (with quotes) to prevent whitespace problems.
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.73813`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and error prevention

**Justification:** The rule prevents unexpected behavior in scripts. While not directly related to error handling or information disclosure, robust code is a prerequisite for secure error handling.

**Caveat:** The relationship is very tenuous and primarily functional.

### shellcheck:SC2049:rank_1:SR 3.5

- Source rule: `SC2049` — =~ is for regex, but this looks like a glob. Use = instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation and correct interpretation of input

**Justification:** SC2049 warns about incorrect regex usage that could lead to unintended matching behavior. SR 3.5 requires validation of input syntax to prevent security issues. Ensuring that input matching logic (regex vs glob) is correctly implemented is a fundamental aspect of secure input processing.

**Caveat:** While the rule is a coding best practice, it directly supports the requirement to validate the syntax of inputs used by the control system.

### shellcheck:SC2050:rank_1:SR 3.5

- Source rule: `SC2050` — This expression is constant. Did you forget the $ on a variable?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and logic integrity

**Justification:** The rule identifies logic errors where variables are treated as literals, which can lead to bypasses in security checks (e.g., an 'if' condition that is always false or true). While not direct input validation, it ensures that security-critical logic actually evaluates the intended input.

**Caveat:** The rule is primarily a code quality/correctness rule, not a dedicated input validation security control.

### shellcheck:SC2051:rank_2:SR 3.5

- Source rule: `SC2051` — Bash doesn't support variables in brace range expansions.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.990313`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC2051 is primarily a syntax issue, the rationale mentions that using 'eval' to work around brace expansion limitations can be dangerous if the input is user-controlled. This touches upon the need to validate inputs to prevent command injection, which is relevant to SR 3.5.

**Caveat:** The rule itself is about syntax, not security, but the suggested workarounds involve security risks.

### shellcheck:SC2053:rank_1:SR 3.2 RE 1

- Source rule: `SC2053` — Quote the rhs of = in [[ ]] to prevent glob matching.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and integrity

**Justification:** While the rule prevents unintended glob matching (a form of input sanitization), it is a general coding practice rather than a specific mechanism for malicious code protection at entry/exit points.

**Caveat:** Could be considered a minor defense-in-depth measure against injection, but is not a primary control for SR 3.2.

### shellcheck:SC2053:rank_6:SR 3.5

- Source rule: `SC2053` — Quote the rhs of = in [[ ]] to prevent glob matching.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.864713`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `indirect`

**Security objective:** Input validation and sanitization

**Justification:** The rule prevents unintended glob expansion in shell comparisons, which is a form of input validation. By ensuring variables are treated as literal strings rather than patterns, it prevents unexpected behavior when processing inputs.

**Caveat:** This is a low-level coding practice that contributes to the broader goal of input validation.

### shellcheck:SC2053:rank_9:SR 2.4

- Source rule: `SC2053` — Quote the rhs of = in [[ ]] to prevent glob matching.
- Rank: `9`
- IEC target: `SR 2.4` — Mobile code
- Relative score: `0.819729`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `code execution security`
- Directness: `indirect`

**Security objective:** Mobile code security

**Justification:** While the rule is about shell script syntax, improper handling of variables in scripts can lead to command injection or unintended execution paths, which is relevant to the broader security of mobile or interpreted code.

**Caveat:** The relationship is weak as the rule is specific to shell globbing rather than general mobile code execution policies.

### shellcheck:SC2054:rank_1:SR 3.5

- Source rule: `SC2054` — Use spaces, not commas, to separate array elements.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** SC2054 prevents syntax errors in array definitions. While it ensures the command receives the intended arguments, it is a general coding practice rather than a security-focused input validation mechanism against malicious content.

**Caveat:** The rule prevents unintended command execution behavior, which is tangentially related to input processing.

### shellcheck:SC2055:rank_1:SR 3.5

- Source rule: `SC2055` — You probably wanted && here, otherwise it's always true.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule identifies a logical error in conditional checks that validate input values, which is a fundamental aspect of input validation.

**Caveat:** The rule is a general programming best practice, but it directly impacts the correctness of input validation logic.

### shellcheck:SC2056:rank_1:SR 3.5

- Source rule: `SC2056` — You probably wanted && here
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule identifies a logical error in conditional checks that validate input values, which is a fundamental aspect of input validation.

**Caveat:** The rule is a general programming best practice, but it directly impacts the correctness of input validation logic.

### shellcheck:SC2056:rank_4:SR 3.7

- Source rule: `SC2056` — You probably wanted && here
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.79573`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `logical_error_vs_error_handling`
- Directness: `indirect`

**Security objective:** Correctness of logical conditions

**Justification:** While the rule is a general logic fix, incorrect conditional logic can lead to improper error handling or unexpected control flow, which is relevant to the broader scope of robust error handling.

**Caveat:** The rule is a general programming best practice and not specifically targeted at security-sensitive error handling.

### shellcheck:SC2057:rank_4:SR 3.7

- Source rule: `SC2057` — Unknown binary operator.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.748402`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling

**Justification:** While the rule is a syntax check, improper handling of unknown operators in scripts can lead to unexpected script behavior or crashes, which relates to the broader concept of system robustness and error handling.

**Caveat:** The relationship is very weak as the rule is primarily a linter check for typos rather than a security-focused error handling mechanism.

### shellcheck:SC2058:rank_1:SR 3.7

- Source rule: `SC2058` — Unknown unary operator.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling

**Justification:** Similar to SC2057, this rule identifies a syntax error. Ensuring scripts do not fail due to syntax errors contributes to the reliability of error handling routines, though it is not a direct security control.

**Caveat:** The relationship is weak; this is a general code quality rule.

### shellcheck:SC2059:rank_2:SR 3.5

- Source rule: `SC2059` — SC2059
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.970805`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation and injection prevention

**Justification:** SC2059 prevents format string injection, which is a specific form of input validation failure where untrusted data is interpreted as a command or format string. This directly supports the requirement to validate input content to prevent unintended interpretation.

**Caveat:** The rule is specific to shell scripting, while the SR is a general control system requirement.

### shellcheck:SC2059:rank_5:SR 3.3

- Source rule: `SC2059` — SC2059
- Rank: `5`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.755577`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and secure coding

**Justification:** The rule prevents format string vulnerabilities, which are a class of software defects. While this improves code robustness, it is not directly related to the verification of security functions as defined in SR 3.3.

**Caveat:** The rule is a general secure coding practice rather than a specific security function verification mechanism.

### shellcheck:SC2059:rank_7:SR 3.7

- Source rule: `SC2059` — SC2059
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.73353`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Secure error handling and input sanitization

**Justification:** Improper use of printf can lead to unexpected behavior or crashes, which could be interpreted as an error condition. However, the rule is primarily about preventing injection/logic errors rather than managing error message disclosure.

**Caveat:** The relationship is weak as the rule focuses on data integrity rather than error message information leakage.

### shellcheck:SC2060:rank_1:SR 3.7

- Source rule: `SC2060` — SC2060
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness and error prevention

**Justification:** The rule prevents unintended command execution due to globbing, which improves script reliability. While this prevents unexpected behavior, it does not directly address the security requirement of handling error conditions to prevent information disclosure.

**Caveat:** The rule is a general reliability improvement, not a security-specific error handling mechanism.

### shellcheck:SC2061:rank_8:SR 3.5

- Source rule: `SC2061` — Quote the parameter to -name so the shell won't interpret it.
- Rank: `8`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.715959`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `indirect`

**Security objective:** Preventing unintended command interpretation

**Justification:** The rule prevents shell expansion from altering the intended input to a command, which aligns with the requirement to validate input syntax to prevent unintended interpretation.

**Caveat:** This is a specific instance of input validation (shell injection/misinterpretation) rather than general industrial process control input validation.

### shellcheck:SC2062:rank_1:SR 3.2 RE 1

- Source rule: `SC2062` — SC2062
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `malicious code protection`
- Directness: `indirect`

**Security objective:** Preventing unintended command execution

**Justification:** While the rule prevents shell globbing, it is a stretch to classify this as 'malicious code protection' at entry/exit points, though it does prevent a form of command injection.

**Caveat:** The rule is primarily about shell correctness, not specifically about detecting or blocking malicious code.

### shellcheck:SC2062:rank_5:SR 3.5

- Source rule: `SC2062` — SC2062
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.731944`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC2062 is primarily about shell globbing, failing to quote inputs passed to interpreters (like grep) can lead to unexpected behavior, which is tangentially related to the principle of validating and sanitizing inputs.

**Caveat:** The rule is primarily a functional bug fix rather than a security-focused input validation mechanism.

### shellcheck:SC2063:rank_2:SR 3.5

- Source rule: `SC2063` — Grep uses regex, but this looks like a glob.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.903381`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct interpretation of input data

**Justification:** The rule identifies a common error where regex is confused with globbing, leading to incorrect input matching. This directly supports SR 3.5 by ensuring that inputs used by the system are validated and interpreted as intended, preventing logic errors that could be exploited.

**Caveat:** The rule is a general coding best practice; its security impact depends on whether the grep command is processing security-sensitive input.

### shellcheck:SC2063:rank_4:SR 3.2

- Source rule: `SC2063` — Grep uses regex, but this looks like a glob.
- Rank: `4`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.696829`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Malicious Code Prevention`
- Directness: `Indirect`

**Security objective:** Prevent unintended code execution

**Justification:** While the rule improves code correctness, it is only tangentially related to malicious code protection. It could be argued that preventing logic errors in scripts reduces the attack surface, but it does not directly provide a mechanism to detect or mitigate malicious code.

**Caveat:** The relationship is weak and relies on the assumption that script correctness is a primary defense against malicious code.

### shellcheck:SC2066:rank_1:SR 3.5

- Source rule: `SC2066` — Since you double-quoted this, it will not word split, and the loop will only run once.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct processing of input data to prevent logic errors.

**Justification:** The rule identifies a logic error where input is incorrectly handled due to quoting, which can lead to unexpected behavior. SR 3.5 requires validation of input syntax and content to ensure the control system behaves as intended.

**Caveat:** The rule is primarily a functional correctness check, but in the context of shell scripts used for system automation, it prevents unintended command execution patterns.

### shellcheck:SC2068:rank_1:SR 3.2 RE 1

- Source rule: `SC2068` — Double quote array expansions to avoid re-splitting elements.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** Improperly quoted array expansions can lead to unintended command execution or globbing, which could be exploited to inject malicious arguments, though the rule is primarily a coding best practice.

**Caveat:** The rule is a general coding practice; its security impact depends on whether the arguments are user-controlled.

### shellcheck:SC2068:rank_2:SR 3.5

- Source rule: `SC2068` — Double quote array expansions to avoid re-splitting elements.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.860038`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `medium`

**Security objective:** Input validation

**Justification:** The rationale for SR 3.5 explicitly mentions that inputs should be pre-screened to prevent content from being unintentionally interpreted as commands. Quoting variables is a fundamental form of input sanitization in shell scripting.

**Caveat:** None

### shellcheck:SC2069:rank_4:SR 3.7

- Source rule: `SC2069` — To redirect stdout+stderr, 2>&1 must be last (or use { cmd > file; } 2>&1 to clarify).
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.817229`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** While SC2069 is a syntax error, improper redirection can lead to error messages being leaked to the terminal instead of being suppressed or logged, which relates to the requirement of not providing exploitable information.

**Caveat:** The rule is primarily about shell correctness, not security-sensitive error handling.

### shellcheck:SC2070:rank_1:SR 3.5

- Source rule: `SC2070` — -n doesn't work with unquoted arguments. Quote or use [[ ]].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct interpretation of input data

**Justification:** The rule prevents logic errors caused by unquoted variables in shell scripts, which can lead to unexpected behavior when processing inputs. This aligns with the requirement to validate the syntax and content of inputs to prevent them from being misinterpreted.

**Caveat:** This is a low-level coding practice that supports the broader requirement of input validation.

### shellcheck:SC2071:rank_1:SR 3.5

- Source rule: `SC2071` — > is for string comparisons. Use -gt instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct interpretation of input data

**Justification:** The rule enforces the use of correct numerical comparison operators instead of lexicographical ones, preventing logic errors when validating numeric inputs. This directly supports the requirement to validate the content of inputs used by the control system.

**Caveat:** None

### shellcheck:SC2071:rank_2:SR 2.9 RE 1

- Source rule: `SC2071` — > is for string comparisons. Use -gt instead.
- Rank: `2`
- IEC target: `SR 2.9 RE 1` — Warn when audit record storage capacity threshold reached
- Relative score: `0.742065`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Indirect`

**Security objective:** Audit storage management

**Justification:** While the rule relates to numerical comparison, which might be used in logic checking audit storage thresholds, the rule itself is a general coding practice and not specific to audit record management.

**Caveat:** The relationship is purely coincidental based on the use of numerical comparison logic.

### shellcheck:SC2072:rank_1:SR 3.5

- Source rule: `SC2072` — Decimals are not supported. Either use integers only, or use bc or awk to compare.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct processing of numeric inputs to prevent logic errors.

**Justification:** The rule enforces correct syntax for numeric comparisons, which is a fundamental aspect of validating input content to ensure the control system behaves as expected.

**Caveat:** The rule is primarily a functional correctness check, but in a security context, ensuring inputs are processed as intended prevents logic bypasses.

### shellcheck:SC2072:rank_4:SR 3.7

- Source rule: `SC2072` — Decimals are not supported. Either use integers only, or use bc or awk to compare.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.756164`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Error Handling`
- Directness: `Indirect`

**Security objective:** Prevent unexpected system behavior due to malformed input.

**Justification:** While the rule is about syntax, improper handling of numeric inputs could lead to runtime errors that might be considered part of error handling, though it is a stretch.

**Caveat:** The rule is a static analysis check for syntax, not a runtime error handling mechanism.

### shellcheck:SC2074:rank_1:SR 3.5

- Source rule: `SC2074` — Can't use =~ in [ ]. Use [[..]] instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_correctness_vs_input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell syntax, using the correct test construct (e.g., [[..]] for regex) is a prerequisite for implementing robust input validation logic in shell scripts.

**Caveat:** The rule itself is a syntax fix, not a validation logic implementation.

### shellcheck:SC2075:rank_3:SR 3.5

- Source rule: `SC2075` — Escaping \< is required in [..], but invalid in [[..]]
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.873205`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and prevention of unintended command interpretation

**Justification:** While the rule is primarily about syntax correctness, it touches on how inputs are interpreted by the shell. Misinterpretation of shell operators can lead to logic errors that might be exploited, aligning loosely with the goal of preventing unintended command execution.

**Caveat:** The rule is a linter check for syntax, not a security-focused input validation mechanism.

### shellcheck:SC2076:rank_1:SR 3.5

- Source rule: `SC2076` — Don't quote rhs of =~, it'll match literally rather than as a regex.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation and correct interpretation of regex patterns

**Justification:** The rule ensures that regex patterns are correctly interpreted rather than treated as literal strings, which is a form of input validation to ensure the logic behaves as intended and prevents unexpected behavior in control system inputs.

**Caveat:** While the rule is about syntax, it directly impacts the correctness of input validation logic.

### shellcheck:SC2076:rank_3:SR 3.2 RE 1

- Source rule: `SC2076` — Don't quote rhs of =~, it'll match literally rather than as a regex.
- Rank: `3`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.783364`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `malicious code protection`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** Ensuring regex patterns are correctly parsed is a defensive coding practice that can prevent logic errors, but it is not a direct mechanism for malicious code protection at entry/exit points.

**Caveat:** The relationship is weak as the rule is a general coding best practice rather than a security mechanism.

### shellcheck:SC2076:rank_4:SR 3.3

- Source rule: `SC2076` — Don't quote rhs of =~, it'll match literally rather than as a regex.
- Rank: `4`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.758023`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `security functionality verification`
- Directness: `indirect`

**Security objective:** Code correctness

**Justification:** Correctly implementing regex logic is part of ensuring security functions operate as intended, but the rule itself is a static analysis check, not a verification function for security requirements.

**Caveat:** The rule helps ensure code quality, which supports the reliability of security functions.

### shellcheck:SC2077:rank_6:SR 3.5

- Source rule: `SC2077` — You need spaces around the comparison operator.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.853528`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** While the rule is primarily about shell syntax, it touches on the concept of how inputs are interpreted by a shell. SR 3.5 requires validating input to prevent unintended interpretation, which is tangentially related to ensuring shell commands are parsed as intended.

**Caveat:** The rule is a static analysis check for code correctness, not a security-focused input validation mechanism for industrial process control inputs.

### shellcheck:SC2078:rank_1:SR 3.5

- Source rule: `SC2078` — This expression is constant. Did you forget a $ somewhere?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and logic correctness

**Justification:** While the rule is primarily about fixing coding errors (missing variable expansion), it relates to the broader concept of ensuring that inputs (variables) are correctly evaluated rather than treated as literal strings, which is a prerequisite for robust input validation.

**Caveat:** The rule is a static analysis check for developer error rather than a security-focused input validation mechanism as described in SR 3.5.

### shellcheck:SC2080:rank_10:SR 3.5

- Source rule: `SC2080` — Numbers with leading 0 are considered octal.
- Rank: `10`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.824699`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule identifies an issue where input (a number with a leading zero) is misinterpreted by the shell interpreter. This is a form of input validation failure where the syntax of the input leads to unintended behavior, which aligns with the requirement to validate input syntax to prevent misinterpretation.

**Caveat:** The rule is specific to shell arithmetic, while SR 3.5 is broader, but the underlying principle of preventing interpreter misinterpretation is shared.

### shellcheck:SC2081:rank_1:SR 3.5

- Source rule: `SC2081` — [ .. ] can't match globs. Use [[ .. ]] or grep.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure input syntax is validated to prevent unintended interpretation.

**Justification:** The rule enforces correct syntax for pattern matching in shell scripts, which is a fundamental aspect of input validation to ensure data is processed as intended rather than being misinterpreted by the shell interpreter.

**Caveat:** None

### shellcheck:SC2081:rank_6:SR 3.7

- Source rule: `SC2081` — [ .. ] can't match globs. Use [[ .. ]] or grep.
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.751694`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and input validation

**Justification:** The rule addresses a syntax error in shell scripting that prevents correct glob matching. While this relates to input validation (a component of error handling), it is a language-specific syntax issue rather than a systemic error handling strategy as defined by SR 3.7.

**Caveat:** The rule is a coding best practice for shell scripts, whereas SR 3.7 is a high-level architectural requirement for control systems.

### shellcheck:SC2082:rank_1:SR 1.4

- Source rule: `SC2082` — To expand via indirection, use name="foo$n"; echo "${!name}".
- Rank: `1`
- IEC target: `SR 1.4` — Identifier management
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Identifier management

**Justification:** The rule discusses dynamic variable expansion and warns about the use of 'eval' to avoid arbitrary code execution. While this relates to secure coding, it is only tangentially related to the management of user/group identifiers as required by SR 1.4.

**Caveat:** The rule's mention of 'eval' security risks is relevant to general system security, but the primary focus of the rule is on variable expansion syntax, not identity management.

### shellcheck:SC2082:rank_3:SR 3.5

- Source rule: `SC2082` — To expand via indirection, use name="foo$n"; echo "${!name}".
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.80621`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule explicitly warns about the risks of using 'eval' or dynamic variable expansion without sanitization, which is a form of input validation to prevent arbitrary code execution.

**Caveat:** The rule is specific to shell scripting, while SR 3.5 is a general requirement for control system inputs.

### shellcheck:SC2084:rank_1:SR 3.2 RE 1

- Source rule: `SC2084` — Remove $ or use _=$((expr)) to avoid executing output.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** The rule prevents unintended command execution resulting from shell expansion. While this is a coding best practice to prevent arbitrary code execution, it is a general software robustness issue rather than a specific malicious code protection mechanism at an entry/exit point.

**Caveat:** The rule is a general coding practice, not a dedicated security mechanism.

### shellcheck:SC2084:rank_3:SR 3.5

- Source rule: `SC2084` — Remove $ or use _=$((expr)) to avoid executing output.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.901843`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Prevent unintended command execution from data inputs

**Justification:** The rule prevents the shell from interpreting the result of an arithmetic expansion as a command, which is a form of input validation/sanitization to prevent unintended code execution.

**Caveat:** The rule is specific to shell scripting environments.

### shellcheck:SC2084:rank_4:SR 3.7

- Source rule: `SC2084` — Remove $ or use _=$((expr)) to avoid executing output.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.88061`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Error Handling`
- Directness: `Indirect`

**Security objective:** Prevent information leakage through error messages

**Justification:** While the rule prevents an error (command not found), it is primarily a functional correctness issue rather than an error handling security requirement.

**Caveat:** The rule prevents an error from occurring rather than managing the disclosure of an error.

### shellcheck:SC2084:rank_7:SR 2.4 RE 1

- Source rule: `SC2084` — Remove $ or use _=$((expr)) to avoid executing output.
- Rank: `7`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.780249`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Code Integrity`
- Directness: `Indirect`

**Security objective:** Prevent unauthorized code execution

**Justification:** The rule prevents the shell from executing arbitrary data as code, which is tangentially related to ensuring that only intended code is executed.

**Caveat:** The rule is a syntax/logic check, not a cryptographic integrity check as implied by SR 2.4.

### shellcheck:SC2086:rank_1:SR 3.5

- Source rule: `SC2086` — Double quote to prevent globbing and word splitting.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** Unquoted variables in shell scripts are a common source of command injection and unexpected behavior when inputs contain spaces or glob characters. Quoting variables is a fundamental practice for validating and sanitizing input before it is processed by the shell.

**Caveat:** While this is a best practice for input handling, it is a specific implementation detail rather than a comprehensive input validation framework.

### shellcheck:SC2086:rank_2:SR 7.1 RE 1

- Source rule: `SC2086` — Double quote to prevent globbing and word splitting.
- Rank: `2`
- IEC target: `SR 7.1 RE 1` — Manage communication loads
- Relative score: `0.997345`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Manage communication loads

**Justification:** The rule mentions that unquoted variables can lead to DoS scenarios (e.g., when a variable contains many glob characters). While this is a form of resource exhaustion, it is not directly related to managing communication loads or rate limiting.

**Caveat:** The link to DoS is mentioned in the rule's exceptions, but the primary purpose of the rule is input sanitization, not load management.

### shellcheck:SC2086:rank_4:SR 3.2 RE 1

- Source rule: `SC2086` — Double quote to prevent globbing and word splitting.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.829072`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input sanitization and shell injection prevention

**Justification:** While SC2086 is primarily about shell correctness, improper quoting can lead to command injection vulnerabilities, which is a form of malicious code execution. However, it is not a direct mechanism for malicious code protection at entry/exit points as defined in the requirement.

**Caveat:** The rule is a coding best practice that reduces attack surface but is not a dedicated malicious code protection mechanism.

### shellcheck:SC2087:rank_1:SR 7.1

- Source rule: `SC2087` — Quote EOF to make here document expansions happen on the server side rather than on the client.
- Rank: `1`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct execution context and command injection prevention

**Justification:** The rule prevents unintended local expansion of variables in remote commands, which is a security best practice. However, it does not directly relate to operating in a degraded mode during a DoS event.

**Caveat:** The relationship is purely coincidental based on the broad scope of security hardening.

### shellcheck:SC2089:rank_1:SR 3.5

- Source rule: `SC2089` — SC2089
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** SC2089 warns against improper handling of arguments that can lead to command injection (e.g., via eval). This directly aligns with the SR 3.5 requirement to prevent inputs from being unintentionally interpreted as commands.

**Caveat:** The rule is specific to shell scripting, whereas SR 3.5 is a general control system requirement.

### shellcheck:SC2089:rank_3:SR 3.7

- Source rule: `SC2089` — SC2089
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.7973`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and secure command execution

**Justification:** The rule prevents command injection by ensuring proper quoting, which is a form of input handling. While SR 3.7 focuses on error handling, improper input handling often leads to exploitable error conditions or unexpected system states.

**Caveat:** The primary objective of the rule is preventing code injection, not specifically error handling.

### shellcheck:SC2089:rank_7:SR 7.1

- Source rule: `SC2089` — SC2089
- Rank: `7`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `0.723059`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** System stability and integrity

**Justification:** Command injection vulnerabilities can be used to trigger Denial of Service (DoS) conditions. Preventing such vulnerabilities contributes to overall system resilience.

**Caveat:** The rule is a general secure coding practice, not a specific DoS mitigation mechanism.

### shellcheck:SC2089:rank_8:SR 7.7

- Source rule: `SC2089` — SC2089
- Rank: `8`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.703008`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and secure command execution

**Justification:** SC2089 warns against improper shell variable expansion which can lead to command injection. While this is a security best practice, it is a coding-level vulnerability prevention rather than a system-level capability to restrict unnecessary functions or services as defined in SR 7.7.

**Caveat:** The rule prevents vulnerabilities that could be exploited to bypass restrictions, but it does not directly implement the 'least functionality' requirement.

### shellcheck:SC2091:rank_1:SR 3.5

- Source rule: `SC2091` — Remove surrounding $() to avoid executing output (or use eval if intentional).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** SC2091 warns against unintended command execution via command substitution. While this is a code quality issue, it is closely related to the risk of command injection, which SR 3.5 aims to mitigate by validating inputs.

**Caveat:** The rule is primarily a functional bug fix, but it prevents a class of vulnerabilities that could be exploited if the input to the command substitution is attacker-controlled.

### shellcheck:SC2092:rank_3:SR 3.2 RE 1

- Source rule: `SC2092` — Remove backticks to avoid executing output.
- Rank: `3`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.697966`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code execution safety / Malicious code protection

**Justification:** While SC2092 is a coding best practice to prevent unintended execution, it is not a malicious code protection mechanism. However, preventing unintended execution can be considered a defense-in-depth measure against code injection at entry points.

**Caveat:** The rule is a general coding error prevention, not a security control for entry/exit points.

### shellcheck:SC2093:rank_9:SR 3.7

- Source rule: `SC2093` — Remove exec  if script should continue after this command.
- Rank: `9`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.843185`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule identifies a logic error where a script fails to execute subsequent commands. While this is a functional error, it could be argued that improper script execution flow is a form of error handling, though it is not related to the security-sensitive error reporting described in SR 3.7.

**Caveat:** The rule is a general coding best practice, not a security-focused error handling mechanism.

### shellcheck:SC2094:rank_1:SR 7.3

- Source rule: `SC2094` — Make sure not to read and write the same file in the same pipeline.
- Rank: `1`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Data integrity and availability

**Justification:** The rule prevents data loss due to race conditions during file operations. While this supports general system stability, it is not directly related to the specific requirement of backing up system state information.

**Caveat:** The rule prevents accidental file corruption, which is a prerequisite for reliable backups, but the rule itself is not a backup mechanism.

### shellcheck:SC2095:rank_4:SR 7.1

- Source rule: `SC2095` — Use ssh -n to prevent ssh from swallowing stdin.
- Rank: `4`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `0.869677`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Resource availability and process stability

**Justification:** The rule prevents a script from failing due to unexpected input consumption, which could be viewed as a minor availability issue. However, it is not a DoS protection mechanism in the context of IEC 62443-3-3, which focuses on network-level resilience.

**Caveat:** The relationship is purely incidental; the rule is a coding best practice, not a security control against DoS attacks.

### shellcheck:SC2095:rank_5:SR 3.2 RE 1

- Source rule: `SC2095` — Use ssh -n to prevent ssh from swallowing stdin.
- Rank: `5`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.825712`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** The rule prevents unintended input consumption, which is a robustness issue. While not directly related to malicious code protection, ensuring scripts behave predictably prevents potential logic errors that could be exploited.

**Caveat:** This is a general software robustness issue, not a specific security control against malicious code.

### shellcheck:SC2095:rank_9:SR 3.7

- Source rule: `SC2095` — Use ssh -n to prevent ssh from swallowing stdin.
- Rank: `9`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.729408`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** The rule addresses a logic error in script execution. While it improves script reliability, it does not relate to the security-sensitive error handling requirements defined in SR 3.7.

**Caveat:** The rule is about functional correctness, not security-relevant error handling.

### shellcheck:SC2097:rank_7:SR 4.2 RE 1

- Source rule: `SC2097` — This assignment is only seen by the forked process.
- Rank: `7`
- IEC target: `SR 4.2 RE 1` — Purging of shared memory resources
- Relative score: `0.84088`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Purging of shared memory resources

**Justification:** The rule discusses variable scope and environment variables. While environment variables are a form of shared process state, this rule is about logic errors in script execution, not the secure purging of shared memory to prevent information leakage.

**Caveat:** The relationship is purely coincidental based on the concept of process environment/memory.

### shellcheck:SC2099:rank_1:SR 3.5

- Source rule: `SC2099` — Use $((..)) for arithmetics, e.g. i=$((i + 2))
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** While SC2099 is primarily a functional syntax correction for arithmetic, the rationale mentions that inputs passed to interpreters should be pre-screened to prevent unintended command interpretation, which aligns with the spirit of SR 3.5.

**Caveat:** The rule is primarily about fixing a syntax error to ensure the script runs correctly, rather than a security-focused input validation check.

### shellcheck:SC2100:rank_1:SR 3.5

- Source rule: `SC2100` — Use $((..)) for arithmetics, e.g. i=$((i + 2))
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_input_validation`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax, it touches on how inputs are interpreted. SR 3.5 requires that inputs are not unintentionally interpreted as commands; however, this rule is about internal script logic rather than external process control inputs.

**Caveat:** The rule is a best practice for code correctness, not a security control for input validation.

### shellcheck:SC2103:rank_4:SR 3.7

- Source rule: `SC2103` — Use a ( subshell ) to avoid having to cd back.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.74171`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and robustness

**Justification:** The rule improves script robustness by handling potential failures (cd errors), which aligns with the general principle of robust error handling in SR 3.7, though the rule is not specifically about security-sensitive error disclosure.

**Caveat:** The rule is primarily about functional correctness rather than security-critical error handling.

### shellcheck:SC2106:rank_3:SR 3.7

- Source rule: `SC2106` — This only exits the subshell caused by the pipeline.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.681047`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error_handling_syntax`
- Directness: `indirect`

**Security objective:** Error handling

**Justification:** The rule identifies a logic error where a script fails to handle a condition (the break) correctly due to subshell scoping. While this is a bug, it is a stretch to classify it as an 'error handling' security requirement under IEC 62443-3-3.

**Caveat:** The rule is a coding best practice, not a security-specific error handling mechanism.

### shellcheck:SC2107:rank_1:SR 3.7

- Source rule: `SC2107` — Instead of [ a && b ], use [ a ] && [ b ].
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error_handling_syntax`
- Directness: `indirect`

**Security objective:** Error handling

**Justification:** The rule corrects invalid syntax that would cause a script to fail or behave unexpectedly. Proper syntax is a prerequisite for robust error handling, but this is a general coding issue rather than a security-specific error handling requirement.

**Caveat:** The rule is a coding best practice, not a security-specific error handling mechanism.

### shellcheck:SC2107:rank_4:SR 3.5

- Source rule: `SC2107` — Instead of [ a && b ], use [ a ] && [ b ].
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.850036`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_support`
- Directness: `weak`

**Security objective:** Input validation and robust code execution

**Justification:** While the rule is primarily a syntax fix, ensuring that conditional logic in scripts is correctly parsed prevents unexpected behavior, which is a prerequisite for reliable input validation.

**Caveat:** The rule is a general coding best practice rather than a specific security control for input validation.

### shellcheck:SC2109:rank_1:SR 3.5

- Source rule: `SC2109` — Instead of [ a || b ], use [ a ] || [ b ].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntactic_to_functional`
- Directness: `indirect`

**Security objective:** Input validation and code robustness

**Justification:** While the rule is purely syntactic, ensuring correct shell script logic is a prerequisite for robust input handling. However, it does not directly implement input validation as defined in SR 3.5.

**Caveat:** The rule improves code reliability but does not perform security-relevant input validation.

### shellcheck:SC2110:rank_1:SR 3.5

- Source rule: `SC2110` — In [[..]], use || instead of -o.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `input_validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax fix, ensuring correct logical evaluation in shell scripts is a prerequisite for robust input validation logic. If the logic fails due to syntax errors, input validation checks may be bypassed.

**Caveat:** The rule is a general coding best practice rather than a specific security control.

### shellcheck:SC2114:rank_1:SR 4.2 RE 1

- Source rule: `SC2114` — Warning: deletes a system directory.
- Rank: `1`
- IEC target: `SR 4.2 RE 1` — Purging of shared memory resources
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** System integrity and resource protection

**Justification:** The rule prevents accidental deletion of system directories. While this is a safety/integrity issue, it is only tangentially related to the specific requirement of preventing unauthorized information transfer via shared memory.

**Caveat:** The rule is about file system integrity, not shared memory isolation.

### shellcheck:SC2114:rank_2:SR 4.2

- Source rule: `SC2114` — Warning: deletes a system directory.
- Rank: `2`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `0.744675`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** System integrity and resource protection

**Justification:** The rule prevents accidental deletion of system directories. While this protects system state, it does not directly address the purging of information from decommissioned components as required by SR 4.2.

**Caveat:** The rule is about preventing accidental deletion, not about secure purging of data.

### shellcheck:SC2116:rank_5:SR 3.5

- Source rule: `SC2116` — Useless echo? Instead of cmd $(echo foo), just use cmd foo.
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.786192`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is primarily about code style, the exceptions mention that improper use of echo/subshells can lead to issues with special characters and command injection, which relates to input validation.

**Caveat:** The rule is primarily a linter for code cleanliness, not a security-focused input validator.

### shellcheck:SC2117:rank_1:SR 2.1 RE 3

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `1`
- IEC target: `SR 2.1 RE 3` — Supervisor override
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Privilege management and authorization

**Justification:** The rule addresses how to correctly execute commands as another user (privilege escalation/delegation), which is tangentially related to how a system manages user authorizations and overrides.

**Caveat:** The rule is about shell scripting best practices for privilege switching, not specifically about the supervisor override mechanism defined in SR 2.1.

### shellcheck:SC2117:rank_2:SR 2.1 RE 1

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `2`
- IEC target: `SR 2.1 RE 1` — Authorization enforcement for all users
- Relative score: `0.993364`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Access Control`
- Directness: `Direct`

**Security objective:** Enforce authorization and least privilege

**Justification:** The rule ensures that commands are executed with the intended user privileges, which is a fundamental aspect of enforcing authorization and least privilege as required by SR 2.1.

**Caveat:** The rule is specific to shell scripting environments.

### shellcheck:SC2117:rank_3:SR 2.12 RE 1

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `3`
- IEC target: `SR 2.12 RE 1` — Non-repudiation for all users
- Relative score: `0.985695`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Accountability`
- Directness: `Indirect`

**Security objective:** Non-repudiation

**Justification:** While using sudo/su correctly helps ensure the correct user identity is associated with an action, the rule itself is primarily about privilege management rather than audit logging or non-repudiation.

**Caveat:** The relationship is weak; proper user context is a prerequisite for non-repudiation but not the mechanism itself.

### shellcheck:SC2117:rank_6:SR 2.1 RE 2

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `6`
- IEC target: `SR 2.1 RE 2` — Permission mapping to roles
- Relative score: `0.886524`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Access Control`
- Directness: `Indirect`

**Security objective:** Role-based access control

**Justification:** The rule ensures commands run with the correct user context, which is related to the enforcement of roles, but it does not address the definition or mapping of permissions to roles.

**Caveat:** The rule is about execution context, not policy definition.

### shellcheck:SC2117:rank_8:SR 2.1

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `8`
- IEC target: `SR 2.1` — Authorization enforcement
- Relative score: `0.81831`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supporting`
- Directness: `indirect`

**Security objective:** Authorization enforcement

**Justification:** Using sudo correctly ensures that commands are executed with the intended privileges, which is a fundamental aspect of enforcing authorization and least privilege as required by SR 2.1.

**Caveat:** The rule is a best practice for script execution, not a direct implementation of an authorization enforcement mechanism.

### shellcheck:SC2117:rank_10:SR 1.1

- Source rule: `SC2117` — To run commands as another user, use su -c or sudo.
- Rank: `10`
- IEC target: `SR 1.1` — Human user identification and authentication
- Relative score: `0.748443`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `supporting`
- Directness: `indirect`

**Security objective:** User identification and authentication

**Justification:** The rule ensures that commands are run as the correct user, which is related to maintaining the integrity of the user identity context, but it does not address the authentication process itself.

**Caveat:** The rule is about privilege escalation, not the identification or authentication of the user.

### shellcheck:SC2120:rank_2:SR 3.5

- Source rule: `SC2120` — SC2120
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.985938`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC2120 is primarily about code correctness, ensuring that functions receive the correct parameters is a prerequisite for robust input handling. However, it is not a security-focused input validation mechanism.

**Caveat:** The rule is a functional correctness check, not a security validation check.

### shellcheck:SC2122:rank_1:SR 3.5

- Source rule: `SC2122` — >= is not a valid operator. Use ! a < b instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Correct implementation of logical comparisons

**Justification:** While the rule is primarily a syntax fix for shell operators, incorrect logical comparisons in scripts can lead to flawed input validation or logic errors that impact system security.

**Caveat:** The rule is a general syntax correction, not a specific security-focused input validation check.

### shellcheck:SC2124:rank_2:SR 3.5

- Source rule: `SC2124` — Assigning an array to a string! Assign as array, or use * instead of @ to concatenate.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.949558`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax correctness, improper handling of array-to-string conversions can lead to unexpected data structures, which in some contexts could be considered a form of input handling error. However, this is a stretch as it is a language-specific coding bug rather than a security-focused input validation mechanism.

**Caveat:** The relationship is very weak and primarily functional.

### shellcheck:SC2125:rank_1:SR 3.5

- Source rule: `SC2125` — Brace expansions and globs are literal in assignments. Quote it or use an array.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule prevents unintended literal assignment of glob patterns, which can be a form of input handling error. While not a direct input validation of external data, it ensures that variables intended to hold dynamic paths or values are correctly assigned, preventing logic errors that could lead to unexpected system behavior.

**Caveat:** This is a coding best practice for shell scripts rather than a direct security control for input validation of external data.

### shellcheck:SC2126:rank_4:SR 3.7

- Source rule: `SC2126` — Consider using grep -c instead of grep | wc
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.870741`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `error_handling_best_practice`
- Directness: `indirect`

**Security objective:** Error handling

**Justification:** The rule mentions that using 'grep -c' instead of piping to 'wc' allows for better handling of exit codes, which is a form of error handling. However, this is a minor coding practice rather than a security-focused error handling mechanism.

**Caveat:** The relationship is weak as the rule is primarily stylistic.

### shellcheck:SC2127:rank_4:SR 3.5

- Source rule: `SC2127` — To use ${ ..; }, specify #!/usr/bin/env ksh.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.8209`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax compatibility, ensuring that scripts are executed by the correct interpreter can prevent unexpected behavior when processing inputs, which is tangentially related to robust input handling.

**Caveat:** The rule is fundamentally about portability, not security-focused input validation.

### shellcheck:SC2130:rank_1:SR 3.7

- Source rule: `SC2130` — -eq is for integer comparisons. Use = instead.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and error handling

**Justification:** Using the wrong comparison operator can lead to unexpected logic branches or runtime errors. While this relates to code correctness, it is only tangentially related to the security-focused error handling requirements of SR 3.7.

**Caveat:** The rule is primarily a bug-prevention measure rather than a security-specific error handling mechanism.

### shellcheck:SC2130:rank_6:SR 3.5

- Source rule: `SC2130` — -eq is for integer comparisons. Use = instead.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.746316`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax check, it relates to ensuring that data is treated as the correct type (string vs integer), which is a fundamental aspect of input validation and preventing unexpected interpretation of data.

**Caveat:** The rule is a static analysis check for shell scripting best practices rather than a security-focused input validation mechanism for industrial control inputs.

### shellcheck:SC2139:rank_10:SR 3.5

- Source rule: `SC2139` — This expands when defined, not when used. Consider escaping.
- Rank: `10`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.819827`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule prevents unintended shell expansion, which is a form of input handling. While not direct input validation, it relates to the rationale of SR 3.5 regarding preventing content from being unintentionally interpreted as commands.

**Caveat:** The rule is primarily about shell syntax, not industrial process control input validation.

### shellcheck:SC2140:rank_2:SR 3.7

- Source rule: `SC2140` — Word is of the form "A"B"C" (B indicated). Did you mean "ABC" or "A\"B\"C"?
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.921684`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and secure output formatting

**Justification:** The rule identifies potential syntax errors in shell scripts that could lead to malformed output. While this relates to the integrity of generated data, it is a stretch to link it directly to the security requirement of handling error conditions without leaking sensitive information.

**Caveat:** The rule is primarily a code quality/syntax check rather than a security-focused error handling mechanism.

### shellcheck:SC2140:rank_4:SR 3.5

- Source rule: `SC2140` — Word is of the form "A"B"C" (B indicated). Did you mean "ABC" or "A\"B\"C"?
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.835095`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule detects malformed strings which could be interpreted as commands or unintended data. This is tangentially related to input validation, as improper quoting can lead to injection-like vulnerabilities in shell scripts.

**Caveat:** The rule is more about syntax correctness than robust security-focused input validation.

### shellcheck:SC2141:rank_1:SR 3.5

- Source rule: `SC2141` — Did you mean IFS=$'\t' ?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and correct interpretation

**Justification:** The rule ensures that shell scripts correctly interpret input delimiters (tabs vs literal characters). While this is a coding best practice, it is only tangentially related to the security requirement of validating industrial process control inputs.

**Caveat:** The rule is a general coding correctness issue rather than a security-focused input validation mechanism.

### shellcheck:SC2145:rank_1:SR 3.5

- Source rule: `SC2145` — Argument mixes string and array. Use * or separate argument.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule prevents unexpected behavior when handling arrays/strings in shell scripts. While not a direct security validation, improper handling of inputs in scripts can lead to command injection or logic errors, which relates to the broader goal of input validation.

**Caveat:** The rule is primarily a code correctness/best practice warning rather than a security-focused input validation check.

### shellcheck:SC2145:rank_4:SR 3.7

- Source rule: `SC2145` — Argument mixes string and array. Use * or separate argument.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.843739`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and information disclosure prevention

**Justification:** The rule prevents unintended shell expansion behavior that could lead to malformed error messages or unexpected script execution. While not a direct security control, ensuring error messages are correctly formatted supports the requirement to handle errors without leaking exploitable information.

**Caveat:** The rule is primarily a code correctness/best practice rule rather than a dedicated security control.

### shellcheck:SC2146:rank_3:SR 7.3

- Source rule: `SC2146` — This action ignores everything before the -o. Use \( \) to group.
- Rank: `3`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.811697`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code correctness and logic grouping

**Justification:** While the rule is a general coding error, the example provided involves a 'find' command used for file operations (copying), which could theoretically be part of a backup script. However, the rule itself does not enforce backup integrity or availability.

**Caveat:** The relationship is purely coincidental based on the example code provided in the rule description.

### shellcheck:SC2148:rank_1:SR 3.8 RE 3

- Source rule: `SC2148` — Tips depend on target shell and yours is unknown. Add a shebang.
- Rank: `1`
- IEC target: `SR 3.8 RE 3` — Randomness of session IDs
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Script execution environment consistency

**Justification:** The rule ensures the script runs in the intended shell, which is a prerequisite for reliable behavior, including the use of random number generators. However, it does not directly implement the requirement for secure session ID generation.

**Caveat:** The rule is a best practice for script reliability, not a security control for session ID generation.

### shellcheck:SC2149:rank_6:SR 3.5

- Source rule: `SC2149` — Remove $/${} for numeric index, or escape it for string.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.923254`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC2149 is primarily a syntax rule, the rationale mentions preventing accidental dereferencing of variables, which is a form of input handling that could prevent unintended command execution in specific shell contexts.

**Caveat:** The rule is primarily about shell syntax correctness rather than security-focused input validation.

### shellcheck:SC2150:rank_1:SR 3.3

- Source rule: `SC2150` — -exec does not automatically invoke a shell. Use -exec sh -c .. for that.
- Rank: `1`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and secure command execution

**Justification:** The rule prevents command injection by enforcing secure argument handling in shell scripts. While this is a general secure coding practice, it is only tangentially related to the verification of security functions (SR 3.3) unless the script itself is part of a security verification tool.

**Caveat:** The rule is a general security best practice, not a specific verification mechanism.

### shellcheck:SC2150:rank_4:SR 1.13 RE 1

- Source rule: `SC2150` — -exec does not automatically invoke a shell. Use -exec sh -c .. for that.
- Rank: `4`
- IEC target: `SR 1.13 RE 1` — Explicit access request approval
- Relative score: `0.873969`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Access control and input sanitization

**Justification:** While the rule prevents command injection, it is a local code-level issue. SR 1.13 relates to network-level access requests, though preventing injection is a prerequisite for secure access handling.

**Caveat:** The scope of the rule is local execution, whereas the requirement is network-centric.

### shellcheck:SC2150:rank_7:SR 3.7

- Source rule: `SC2150` — -exec does not automatically invoke a shell. Use -exec sh -c .. for that.
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.825114`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and secure coding

**Justification:** Improper command execution can lead to error conditions. While the rule is primarily about injection, it relates to how the system handles unexpected input/execution paths, which is relevant to SR 3.7.

**Caveat:** The rule is specifically about command injection, not general error handling or information disclosure.

### shellcheck:SC2150:rank_9:SR 2.4 RE 1

- Source rule: `SC2150` — -exec does not automatically invoke a shell. Use -exec sh -c .. for that.
- Rank: `9`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.750727`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Prevent command injection / Ensure code integrity

**Justification:** While the rule prevents command injection, it is not specifically about verifying the integrity of mobile code before execution as required by SR 2.4 RE 1. However, preventing injection is a prerequisite for secure code execution.

**Caveat:** The rule is a general coding best practice, not a specific integrity verification mechanism.

### shellcheck:SC2151:rank_5:SR 3.7

- Source rule: `SC2151` — Only one integer 0-255 can be returned. Use stdout for other data.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.790594`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and information disclosure

**Justification:** While SC2151 is primarily about syntax, improper handling of function return values can lead to unexpected program states or incorrect error reporting, which is tangentially related to robust error handling.

**Caveat:** The rule is a best practice for shell scripting, not a security-specific error handling mechanism.

### shellcheck:SC2152:rank_9:SR 3.7

- Source rule: `SC2152` — Can only return 0-255. Other data should be written to stdout.
- Rank: `9`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.730578`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule suggests using stderr for error messages, which aligns with the principle of separating diagnostic information from standard output, potentially aiding in secure error handling.

**Caveat:** The rule is primarily about shell syntax and function design rather than security-focused error handling.

### shellcheck:SC2153:rank_1:SR 3.5

- Source rule: `SC2153` — Possible Misspelling: MYVARIABLE may not be assigned. Did you mean MY_VARIABLE?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule identifies potential bugs (misspelled variables), it is not a security-focused input validation mechanism for external data, which is the focus of SR 3.5.

**Caveat:** This is a code quality check, not a security validation check.

### shellcheck:SC2153:rank_3:SR 3.7

- Source rule: `SC2153` — Possible Misspelling: MYVARIABLE may not be assigned. Did you mean MY_VARIABLE?
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.986627`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness and error handling

**Justification:** SC2153 identifies potential logic errors due to variable misspellings. While this improves code reliability, it is a general software quality issue rather than a specific mechanism for handling security-relevant error conditions as defined in SR 3.7.

**Caveat:** The rule helps prevent unexpected behavior, which is a prerequisite for robust error handling, but it does not address the security-sensitive disclosure of error information.

### shellcheck:SC2154:rank_1:SR 3.5

- Source rule: `SC2154` — var is referenced but not assigned.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and robust error handling

**Justification:** SC2154 identifies unassigned variables, which can lead to unexpected behavior or logic errors in scripts. While not a direct input validation mechanism for external data, ensuring variables are correctly initialized is a defensive programming practice that prevents malformed inputs or logic flaws that could be exploited.

**Caveat:** This rule is primarily a code quality/correctness check rather than a security-focused input validation mechanism.

### shellcheck:SC2154:rank_7:SR 3.7

- Source rule: `SC2154` — var is referenced but not assigned.
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.687661`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and information disclosure

**Justification:** While SC2154 is primarily about code correctness, uninitialized variables can lead to unexpected runtime errors. If these errors are exposed to users, they might leak information about the system's internal state, which relates to the requirement to handle errors without providing exploitable information.

**Caveat:** The rule is not specifically designed to prevent information disclosure, but it is a prerequisite for robust error handling.

### shellcheck:SC2155:rank_1:SR 3.6

- Source rule: `SC2155` — Declare and assign separately to avoid masking return values.
- Rank: `1`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and error propagation

**Justification:** SC2155 ensures that command return values are not masked, which is critical for robust error handling. While SR 3.6 focuses on deterministic output during attacks, the ability to correctly detect and handle failures is a foundational aspect of maintaining system state.

**Caveat:** The rule is a general software engineering best practice rather than a specific security control for deterministic output.

### shellcheck:SC2155:rank_3:SR 5.2 RE 3

- Source rule: `SC2155` — Declare and assign separately to avoid masking return values.
- Rank: `3`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `0.95706`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and failure handling

**Justification:** SC2155 helps ensure that errors are correctly detected. SR 5.2 RE 3 requires the system to fail in a controlled manner. Correct error detection is a necessary component of implementing a 'fail close' mechanism.

**Caveat:** The rule is a general coding practice and does not specifically address boundary protection or fail-close logic.

### shellcheck:SC2155:rank_4:SR 3.2 RE 1

- Source rule: `SC2155` — Declare and assign separately to avoid masking return values.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.954954`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness and error handling in scripts

**Justification:** The rule prevents masking command exit codes, which is a best practice for robust script execution. While not a direct malicious code protection mechanism, it ensures that errors in command execution are not ignored, which is a prerequisite for reliable system operation.

**Caveat:** This is a general software quality rule rather than a specific security control for malicious code protection.

### shellcheck:SC2155:rank_5:SR 3.7

- Source rule: `SC2155` — Declare and assign separately to avoid masking return values.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.899625`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `medium`

**Security objective:** Error handling

**Justification:** The rule directly addresses the masking of return values, which is a fundamental aspect of error handling. By ensuring that command failures are visible, the system can properly identify and handle error conditions as required by SR 3.7.

**Caveat:** The rule is a coding standard; it supports the requirement but does not implement the full error handling logic required by the standard.

### shellcheck:SC2156:rank_1:SR 1.2

- Source rule: `SC2156` — Injecting filenames is fragile and insecure. Use parameters.
- Rank: `1`
- IEC target: `SR 1.2` — Software process and device identification and authentication
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** SC2156 prevents command injection by properly handling parameters. While this is a general security best practice, it is not directly related to the identification and authentication of software processes as defined in SR 1.2.

**Caveat:** While command injection prevention is a prerequisite for secure systems, it does not fulfill the specific requirement of identifying and authenticating entities.

### shellcheck:SC2156:rank_4:SR 3.7

- Source rule: `SC2156` — Injecting filenames is fragile and insecure. Use parameters.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.919926`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Prevent command injection

**Justification:** The rule prevents command injection, which is a security vulnerability. While SR 3.7 focuses on error handling, improper error handling can sometimes leak information or be a side effect of injection vulnerabilities, but the primary goal of the rule is input sanitization, not error management.

**Caveat:** The relationship is weak as the rule addresses input validation/sanitization rather than the specific error handling requirements of SR 3.7.

### shellcheck:SC2156:rank_7:SR 3.2

- Source rule: `SC2156` — Injecting filenames is fragile and insecure. Use parameters.
- Rank: `7`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.880387`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `high`

**Security objective:** Prevent command injection

**Justification:** Command injection is a primary vector for malicious code execution. By enforcing parameterization, the rule acts as a prevention mechanism against unauthorized software execution, which aligns directly with the objectives of SR 3.2.

**Caveat:** While the rule is a coding best practice, it is a specific implementation detail of the broader malicious code protection requirement.

### shellcheck:SC2156:rank_8:SR 3.2 RE 1

- Source rule: `SC2156` — Injecting filenames is fragile and insecure. Use parameters.
- Rank: `8`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.803221`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `medium`

**Security objective:** Prevent command injection

**Justification:** The rule prevents malicious code execution via input injection. If the input is coming from an external entry point, this rule supports the requirement to protect entry points from malicious code.

**Caveat:** The rule is general and not limited to entry/exit points, making the mapping to RE 1 context-dependent.

### shellcheck:SC2157:rank_1:SR 3.5

- Source rule: `SC2157` — Argument to implicit -n is always true due to literal strings.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Ensure correct logic evaluation of input strings

**Justification:** The rule identifies logic errors where input strings are incorrectly evaluated as true/false. While this relates to how inputs are processed, it is a coding logic error rather than the validation of input syntax/content against security policies as intended by SR 3.5.

**Caveat:** The rule prevents logic bypasses, which is a form of input handling, but it is not a direct validation of input content.

### shellcheck:SC2158:rank_1:SR 3.5

- Source rule: `SC2158` — [ false ] is true. Remove the brackets
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Ensure correct logic evaluation of input strings

**Justification:** Similar to SC2157, this rule addresses a logic error where a string is incorrectly evaluated. It is not a direct validation of input syntax or content as required by SR 3.5.

**Caveat:** The rule prevents logic bypasses, which is a form of input handling, but it is not a direct validation of input content.

### shellcheck:SC2159:rank_1:SR 3.5

- Source rule: `SC2159` — [ 0 ] is true. Use false instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and logic correctness

**Justification:** While the rule is primarily a syntax/logic fix, it touches on how inputs are interpreted. If a script incorrectly interprets input as a boolean, it could lead to unexpected control flow, which is tangentially related to the broader goal of robust input handling.

**Caveat:** The rule is a static syntax check, not a comprehensive input validation mechanism as required by SR 3.5.

### shellcheck:SC2162:rank_1:SR 3.5

- Source rule: `SC2162` — read without -r will mangle backslashes.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure input data is read accurately without unintended interpretation of escape characters.

**Justification:** The rule enforces the use of 'read -r' to prevent the shell from interpreting backslashes as escape characters, which is a form of input sanitization. This directly aligns with SR 3.5's requirement to validate the content of input to prevent it from being unintentionally interpreted as commands.

**Caveat:** This is a low-level implementation detail of input handling, but it is a fundamental aspect of secure input processing in shell scripts.

### shellcheck:SC2163:rank_1:SR 3.5

- Source rule: `SC2163` — This does not export FOO. Remove $/${} for that, or use ${var?} to quiet.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule prevents unintended variable expansion in shell scripts, which is a form of syntax validation. While related to input handling, it is a general coding best practice rather than a specific security-focused input validation mechanism for industrial process control inputs.

**Caveat:** The rule is a general shell scripting best practice and does not specifically target industrial process control inputs as defined in SR 3.5.

### shellcheck:SC2163:rank_5:SR 3.7

- Source rule: `SC2163` — This does not export FOO. Remove $/${} for that, or use ${var?} to quiet.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.85382`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** The rule improves the robustness of shell scripts by preventing incorrect variable exports. While this relates to error handling (as noted in the rule's exception regarding ${var?}), it is a minor coding correction rather than a security-focused error handling strategy.

**Caveat:** The rule's connection to error handling is limited to the specific case of variable expansion modifiers.

### shellcheck:SC2166:rank_2:SR 3.5

- Source rule: `SC2166` — Prefer [ p ] && [ q ] as [ p -a q ] is not well-defined.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.955103`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule prevents logic errors when processing user-supplied input, which is a form of defensive programming related to input handling, though it is not a direct input validation mechanism.

**Caveat:** The rule is primarily about syntax correctness rather than validating the content or structure of input.

### shellcheck:SC2166:rank_5:SR 3.7

- Source rule: `SC2166` — Prefer [ p ] && [ q ] as [ p -a q ] is not well-defined.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.922307`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** The rule prevents undefined behavior in scripts, which could theoretically prevent unexpected error conditions, but it is not an error handling mechanism.

**Caveat:** The relationship is very weak and tangential.

### shellcheck:SC2169:rank_3:SR 7.7

- Source rule: `SC2169` — In dash, something is not supported.
- Rank: `3`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.704565`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** System hardening and minimization of attack surface

**Justification:** While SC2169 is a generic portability warning, ensuring that scripts are compatible with specific, minimal shells (like dash) can be part of a broader effort to reduce system complexity and unnecessary functionality, which aligns loosely with the principle of least functionality.

**Caveat:** The relationship is extremely weak as the rule is about syntax portability, not the removal of unnecessary services or protocols.

### shellcheck:SC2170:rank_2:SR 3.5

- Source rule: `SC2170` — Invalid number for -eq. Use = to compare as string (or use $var to expand as a variable).
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.900258`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supporting`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** SR 3.5 requires validation of input syntax and content. SC2170 identifies incorrect usage of operators in shell scripts, which is a form of syntax validation that prevents logic errors or unexpected behavior when processing inputs.

**Caveat:** The rule is a general coding best practice; while it supports input validation, it is not specifically focused on security-critical industrial process inputs.

### shellcheck:SC2171:rank_1:SR 3.5

- Source rule: `SC2171` — Found trailing ] outside test. Add missing [ or quote if intentional.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `3/5`
- Relation type: `input validation`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** The rule identifies malformed syntax that could lead to unintended command execution or logic errors, which aligns with the goal of validating input syntax to prevent exploitation.

**Caveat:** The rule is primarily a syntax checker, but it prevents the misinterpretation of input as commands, which is a core aspect of SR 3.5.

### shellcheck:SC2171:rank_3:SR 3.7

- Source rule: `SC2171` — Found trailing ] outside test. Add missing [ or quote if intentional.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.894012`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `error handling`
- Directness: `indirect`

**Security objective:** Error handling

**Justification:** While the rule identifies syntax errors, it is not an error handling mechanism itself. It is a static analysis tool that helps developers avoid errors, which is tangentially related to robust software development.

**Caveat:** The rule is a development-time check, not a runtime error handling mechanism as described in SR 3.7.

### shellcheck:SC2173:rank_2:SR 5.2 RE 3

- Source rule: `SC2173` — SIGKILL/SIGSTOP can not be trapped.
- Rank: `2`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `0.987051`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** System reliability and fail-safe behavior

**Justification:** The rule prevents undefined behavior in signal handling, which contributes to system stability. While not directly related to boundary protection, ensuring predictable process termination is a prerequisite for reliable fail-safe mechanisms.

**Caveat:** The rule is a general coding best practice for POSIX systems and is not specific to the boundary protection mechanisms described in SR 5.2.

### shellcheck:SC2173:rank_5:SR 3.6

- Source rule: `SC2173` — SIGKILL/SIGSTOP can not be trapped.
- Rank: `5`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `0.772768`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Deterministic system state

**Justification:** Ensuring that signals are handled correctly (or not trapped when impossible) helps maintain the predictability of a process. This is tangentially related to ensuring a system can reach a deterministic state during failure or attack.

**Caveat:** The rule is a low-level coding constraint, while SR 3.6 is a high-level system design requirement.

### shellcheck:SC2174:rank_1:SR 3.2 RE 1

- Source rule: `SC2174` — When used with -p, -m only applies to the deepest directory.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Malicious code protection on entry and exit points

**Justification:** The rule identifies a potential misconfiguration of directory permissions. While improper permissions can facilitate malicious code persistence, the rule itself is a functional warning about command behavior rather than a security control.

**Caveat:** The rule is primarily about command-line utility behavior, not security policy enforcement.

### shellcheck:SC2174:rank_10:SR 7.7

- Source rule: `SC2174` — When used with -p, -m only applies to the deepest directory.
- Rank: `10`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.762439`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Least functionality and secure configuration

**Justification:** While SC2174 is about file permissions, it relates to the broader concept of secure system configuration. SR 7.7 focuses on restricting unnecessary functions, which is a different aspect of system hardening.

**Caveat:** The relationship is weak as the rule is about correct implementation of permissions rather than disabling unnecessary services.

### shellcheck:SC2175:rank_1:SR 3.5

- Source rule: `SC2175` — Quote this invalid brace expansion since it should be passed literally to eval
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `strong`

**Security objective:** Input validation and injection prevention

**Justification:** The rule prevents unsafe evaluation of inputs by enforcing proper quoting. This directly aligns with the SR 3.5 requirement to validate inputs and prevent them from being unintentionally interpreted as commands (e.g., injection attacks).

**Caveat:** None

### shellcheck:SC2178:rank_4:SR 3.5

- Source rule: `SC2178` — Variable was used as an array but is now assigned a string.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.858562`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and data integrity

**Justification:** While the rule is primarily a syntax check, improper variable handling in shell scripts can lead to unexpected command execution or logic errors if the variable is used as an input to a command. However, this is a stretch as the rule is about internal variable type consistency, not external input validation.

**Caveat:** The rule is a static analysis check for code quality, not a security-focused input validation mechanism.

### shellcheck:SC2181:rank_1:SR 5.2 RE 3

- Source rule: `SC2181` — Check exit code directly with e.g. if mycmd;, not indirectly with $?.
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and fail-safe execution

**Justification:** The rule encourages robust script execution by checking exit codes directly, which prevents silent failures. While this improves reliability, it is a general coding practice rather than a specific implementation of a 'fail close' boundary protection mechanism.

**Caveat:** The rule is a general software quality improvement and does not specifically address boundary protection or communication blocking.

### shellcheck:SC2181:rank_3:SR 3.7

- Source rule: `SC2181` — Check exit code directly with e.g. if mycmd;, not indirectly with $?.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.717231`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `medium`

**Security objective:** Error handling

**Justification:** The rule directly addresses how error conditions (exit codes) are handled in scripts. By ensuring exit codes are checked correctly, the script can remediate errors effectively, which aligns with the requirement to identify and handle error conditions.

**Caveat:** The rule focuses on the mechanism of checking, not the content of the error message itself, which is the secondary focus of SR 3.7.

### shellcheck:SC2182:rank_4:SR 3.5

- Source rule: `SC2182` — This printf format string has no variables. Other arguments are ignored.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.787036`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While SC2182 is primarily a syntax error, improper use of printf with user-controlled variables can lead to format string vulnerabilities, which is a subset of input validation concerns.

**Caveat:** The rule as written focuses on missing placeholders rather than malicious input injection, but the underlying mechanism (printf) is a common vector for input-related security issues.

### shellcheck:SC2184:rank_1:SR 4.2 RE 1

- Source rule: `SC2184` — Quote arguments to unset so they're not glob expanded.
- Rank: `1`
- IEC target: `SR 4.2 RE 1` — Purging of shared memory resources
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Purging of shared memory resources

**Justification:** The rule prevents unintended behavior in variable/array unsetting. While it relates to resource management, it is a shell-specific syntax issue rather than a memory purging security control.

**Caveat:** The rule is a coding best practice for shell scripts, not a system-level memory protection mechanism.

### shellcheck:SC2189:rank_5:SR 3.7

- Source rule: `SC2189` — You can't have | between this redirection and the command it should apply to.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.784443`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and code robustness

**Justification:** While the rule identifies a syntax error (which is a form of error handling), it is a static code quality issue rather than a security-focused error handling mechanism designed to prevent information disclosure to adversaries.

**Caveat:** The rule is purely about syntax correctness, not about how the system handles runtime errors or exposes information.

### shellcheck:SC2190:rank_1:SR 3.5

- Source rule: `SC2190` — Elements in associative arrays need index, e.g. array=( [index]=value ) .
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule enforces correct syntax for associative array initialization in shell scripts. While this is a form of 'syntax validation', it is a language-specific correctness issue rather than a security-focused input validation mechanism intended to prevent malicious injection or tampering as described in SR 3.5.

**Caveat:** The rule is a linter check for code correctness, not a security control for external input.

### shellcheck:SC2191:rank_1:SR 3.5

- Source rule: `SC2191` — The = here is literal. To assign by index, use ( [index]=value ) with no spaces. To keep as literal, quote it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Ensure correct parsing of configuration data

**Justification:** The rule addresses syntax errors in shell array assignments. While this is a form of input validation (ensuring the script interprets data as intended), it is a general coding correctness issue rather than a security-focused input validation against malicious or malformed external inputs as described in SR 3.5.

**Caveat:** The rule is primarily about language syntax correctness rather than security-critical input validation.

### shellcheck:SC2192:rank_1:SR 3.5

- Source rule: `SC2192` — This array element has no value. Remove spaces after = or use "" for empty string.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Ensure correct parsing of configuration data

**Justification:** Similar to SC2191, this rule identifies syntax errors that lead to unintended variable assignments. While it ensures the script behaves as the developer intended, it does not address the security-critical validation of external inputs required by SR 3.5.

**Caveat:** The rule is primarily about language syntax correctness rather than security-critical input validation.

### shellcheck:SC2193:rank_1:SR 3.5

- Source rule: `SC2193` — The arguments to this comparison can never be equal. Make sure your syntax is correct.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and logic correctness

**Justification:** While the rule identifies logic bugs in comparisons (often due to malformed input/syntax), it is a general code quality rule rather than a security-focused input validation mechanism for industrial process control inputs.

**Caveat:** The rule helps prevent logic errors that could lead to unexpected behavior, but it does not specifically address the validation of external process control inputs as required by SR 3.5.

### shellcheck:SC2193:rank_4:SR 3.3

- Source rule: `SC2193` — The arguments to this comparison can never be equal. Make sure your syntax is correct.
- Rank: `4`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.689867`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code quality and verification

**Justification:** While SC2193 is a general bug-finding rule, ensuring code correctness is a prerequisite for the reliable operation of security functions mentioned in SR 3.3. However, the rule is not specifically targeted at security function verification.

**Caveat:** The relationship is purely incidental based on general software quality.

### shellcheck:SC2194:rank_2:SR 3.5

- Source rule: `SC2194` — This word is constant. Did you forget the $ on a variable?
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.909217`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and logic correctness

**Justification:** SC2194 flags code that might not be processing intended input (variables) correctly. SR 3.5 requires validation of input syntax and content. While both touch on 'input', SC2194 is a static analysis check for developer error, not a security control for validating external process inputs.

**Caveat:** The rule helps prevent logic errors, but does not implement input validation as defined by the standard.

### shellcheck:SC2195:rank_1:SR 3.5

- Source rule: `SC2195` — This pattern will never match the case statement's word. Double check them.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and logic correctness

**Justification:** The rule identifies logic errors in input matching (case statements). While this is a form of input validation, it is primarily a functional correctness check rather than a security-focused input validation mechanism against malicious input.

**Caveat:** The rule helps ensure that input is processed as intended, which is a prerequisite for secure input handling.

### shellcheck:SC2198:rank_1:SR 3.5

- Source rule: `SC2198` — Arrays don't work as operands in [ ]. Use a loop (or concatenate with * instead of @).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `3/5`
- Relation type: `supporting`
- Directness: `indirect`

**Security objective:** Input validation

**Justification:** The rule identifies a coding error where array expansion in a test condition leads to incorrect logic. This relates to input validation because the code fails to correctly validate the input against an allowed list, potentially allowing invalid inputs to bypass checks.

**Caveat:** The rule is primarily a syntax/logic error, but it directly impacts the correctness of input validation logic.

### shellcheck:SC2198:rank_7:SR 5.2 RE 1

- Source rule: `SC2198` — Arrays don't work as operands in [ ]. Use a loop (or concatenate with * instead of @).
- Rank: `7`
- IEC target: `SR 5.2 RE 1` — Deny by default, allow by exception
- Relative score: `0.680171`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `syntax_error_vs_access_control_logic`
- Directness: `indirect`

**Security objective:** Deny by default, allow by exception

**Justification:** While the rule is a syntax error, the example code provided in the rule (checking if an extension is in an allowed list) is a form of access control logic. If the syntax error causes the check to fail or behave unexpectedly, it could theoretically impact the enforcement of an allow-list.

**Caveat:** The relationship is purely coincidental based on the example code used to illustrate the syntax error, not the rule itself.

### shellcheck:SC2199:rank_1:SR 3.5

- Source rule: `SC2199` — Arrays implicitly concatenate in [[ ]]. Use a loop (or explicit * instead of @).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Ensure correct validation of input data against a set of allowed values.

**Justification:** The rule identifies a logic error where an array is incorrectly compared against a string, leading to a failure in input validation. SR 3.5 explicitly requires the validation of input content, and this rule ensures that the validation logic actually functions as intended.

**Caveat:** None

### shellcheck:SC2199:rank_5:SR 3.8

- Source rule: `SC2199` — Arrays implicitly concatenate in [[ ]]. Use a loop (or explicit * instead of @).
- Rank: `5`
- IEC target: `SR 3.8` — Session integrity
- Relative score: `0.826727`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation / Integrity`
- Directness: `Indirect`

**Security objective:** Session integrity and rejection of invalid session IDs.

**Justification:** While the rule improves code correctness, it is only tangentially related to session integrity. It could theoretically be used to validate session IDs, but the rule itself is generic and not specific to session management.

**Caveat:** The rule is a general coding best practice; its application to session integrity is purely contextual.

### shellcheck:SC2200:rank_1:SR 3.5

- Source rule: `SC2200` — Brace expansions don't work as operands in [ ]. Use a loop.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule addresses a syntax error in shell scripting that leads to incorrect logic. While this is a form of 'input validation' in a broad sense (ensuring the script logic handles inputs correctly), it is primarily a functional correctness issue rather than a security-focused input validation requirement as defined in SR 3.5.

**Caveat:** The rule is a general coding best practice; it does not specifically target malicious input or security-critical data validation.

### shellcheck:SC2201:rank_1:SR 3.5

- Source rule: `SC2201` — Brace expansion doesn't happen in [[ ]]. Use a loop.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** Similar to SC2200, this rule corrects a logic error where brace expansion is not interpreted as expected. While it ensures the script behaves as intended, it is a functional correctness issue rather than a security-focused input validation mechanism.

**Caveat:** The rule is a general coding best practice; it does not specifically target malicious input or security-critical data validation.

### shellcheck:SC2202:rank_1:SR 7.3

- Source rule: `SC2202` — Globs don't work as operands in [ ]. Use a loop.
- Rank: `1`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `code_correctness_vs_system_functionality`
- Directness: `indirect`

**Security objective:** Reliable execution of backup scripts

**Justification:** While the rule ensures a script correctly iterates over files (which could be part of a backup process), it is a general coding best practice rather than a security requirement for backup systems.

**Caveat:** The rule is a general programming fix; it only relates to SR 7.3 if the script being fixed is specifically part of the control system's backup mechanism.

### shellcheck:SC2202:rank_2:SR 7.3 RE 1

- Source rule: `SC2202` — Globs don't work as operands in [ ]. Use a loop.
- Rank: `2`
- IEC target: `SR 7.3 RE 1` — Backup verification
- Relative score: `0.923453`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `code_correctness_vs_system_functionality`
- Directness: `indirect`

**Security objective:** Reliable execution of backup scripts

**Justification:** The rule ensures a script correctly iterates over files. If this script is used to verify backups, the rule helps ensure the verification logic is syntactically correct.

**Caveat:** The rule is a general programming fix; it only relates to RE 1 if the script being fixed is specifically part of the backup verification mechanism.

### shellcheck:SC2202:rank_3:SR 7.3 RE 2

- Source rule: `SC2202` — Globs don't work as operands in [ ]. Use a loop.
- Rank: `3`
- IEC target: `SR 7.3 RE 2` — Backup automation
- Relative score: `0.885231`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `code_correctness_vs_system_functionality`
- Directness: `indirect`

**Security objective:** Reliable execution of backup scripts

**Justification:** The rule ensures a script correctly iterates over files. If this script is used to automate backups, the rule helps ensure the automation logic is syntactically correct.

**Caveat:** The rule is a general programming fix; it only relates to RE 2 if the script being fixed is specifically part of the backup automation mechanism.

### shellcheck:SC2203:rank_1:SR 7.3

- Source rule: `SC2203` — Globs are ignored in [[ ]] except right of =/!=. Use a loop.
- Rank: `1`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct implementation of file operations

**Justification:** The rule ensures that file operations (like checking file existence or properties) are performed correctly. This is a prerequisite for reliable backup scripts, which are required by SR 7.3, but the rule itself is a general coding best practice rather than a specific security control for backup integrity.

**Caveat:** The rule is a general syntax correction; its impact on backup reliability is incidental.

### shellcheck:SC2203:rank_2:SR 7.3 RE 1

- Source rule: `SC2203` — Globs are ignored in [[ ]] except right of =/!=. Use a loop.
- Rank: `2`
- IEC target: `SR 7.3 RE 1` — Backup verification
- Relative score: `0.852097`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct implementation of file operations

**Justification:** Similar to the SR 7.3 mapping, ensuring that file operations are syntactically correct is necessary for the reliability of backup mechanisms. However, this is a general programming correctness issue, not a specific verification mechanism for backup integrity.

**Caveat:** The rule is a general syntax correction; its impact on backup verification is incidental.

### shellcheck:SC2205:rank_1:SR 3.5

- Source rule: `SC2205` — (..) is a subshell. Did you mean [ .. ], a test expression?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input Validation

**Justification:** While the rule is primarily a syntax correction, using incorrect test expressions in shell scripts can lead to logic errors in input validation routines. However, the rule itself is not a security-focused input validation mechanism.

**Caveat:** The rule is a linter warning for syntax, not a security control for input validation.

### shellcheck:SC2206:rank_1:SR 3.5

- Source rule: `SC2206` — Quote to prevent word splitting/globbing, or split robustly with mapfile or read -a.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Prevent command injection and unintended interpretation of input

**Justification:** The rule prevents shell word splitting and globbing, which are common vectors for command injection and unintended interpretation of input data. This directly supports the requirement to validate input syntax and content to prevent malicious interpretation.

**Caveat:** The rule is specific to shell scripting environments.

### shellcheck:SC2207:rank_1:SR 3.5

- Source rule: `SC2207` — Prefer mapfile or read -a to split command output (or quote to avoid splitting).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Prevent command injection and unintended interpretation of input

**Justification:** Similar to SC2206, this rule prevents unsafe command expansion and word splitting, which are critical for ensuring that input data is not interpreted as commands, aligning with SR 3.5.

**Caveat:** The rule is specific to shell scripting environments.

### shellcheck:SC2208:rank_1:SR 3.2 RE 1

- Source rule: `SC2208` — Use [[ ]] or quote arguments to -v to avoid glob expansion.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input sanitization and shell command safety

**Justification:** SC2208 prevents unintended glob expansion which can lead to unexpected behavior or code execution. While this is a form of input sanitization, it is a stretch to map it directly to 'malicious code protection at entry/exit points' as defined in SR 3.2, which typically refers to antivirus or gateway filtering.

**Caveat:** The rule improves code robustness, which is a prerequisite for security, but it is not a dedicated malicious code protection mechanism.

### shellcheck:SC2208:rank_10:SR 3.5

- Source rule: `SC2208` — Use [[ ]] or quote arguments to -v to avoid glob expansion.
- Rank: `10`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.741044`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is primarily about shell syntax, improper handling of variables in shell scripts can lead to unintended command execution or interpretation, which relates to the broader goal of input validation.

**Caveat:** The rule is a syntax/best-practice check rather than a security-focused input validation check.

### shellcheck:SC2210:rank_1:SR 5.2 RE 3

- Source rule: `SC2210` — This is a file redirection. Was it supposed to be a comparison or fd operation?
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness of system operations

**Justification:** The rule identifies potential misconfigurations in file descriptor redirection. While this is a coding error, ensuring correct redirection is critical for system stability and preventing unintended behavior, which aligns loosely with the robustness required for fail-close mechanisms.

**Caveat:** The rule is primarily a syntax/logic check, not a security-specific mechanism for fail-close.

### shellcheck:SC2210:rank_7:SR 3.7

- Source rule: `SC2210` — This is a file redirection. Was it supposed to be a comparison or fd operation?
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.804221`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and remediation

**Justification:** While SC2210 identifies a syntax error, the rule itself is a form of static analysis that helps prevent runtime errors. However, it does not address the security-sensitive handling of error conditions or information disclosure as defined in SR 3.7.

**Caveat:** The rule helps prevent bugs, but does not specifically address the security requirements of error handling.

### shellcheck:SC2210:rank_8:SR 3.5

- Source rule: `SC2210` — This is a file redirection. Was it supposed to be a comparison or fd operation?
- Rank: `8`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.787874`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** SC2210 detects ambiguous syntax that could lead to unintended file operations. While this is a form of validation, it is a syntax check for shell scripts rather than the validation of industrial process control inputs required by SR 3.5.

**Caveat:** The rule is a static syntax check, not a runtime input validation mechanism for process control.

### shellcheck:SC2211:rank_3:SR 3.5

- Source rule: `SC2211` — This is a glob used as a command name. Was it supposed to be in ${..}, array, or is it missing quoting?
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.885172`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While SC2211 is primarily a syntax error, the misuse of globs or command substitution can lead to unintended command execution, which is tangentially related to the broader goal of input validation and preventing command injection.

**Caveat:** The rule is primarily about developer syntax errors rather than malicious input validation.

### shellcheck:SC2213:rank_1:SR 3.7

- Source rule: `SC2213` — getopts specified -n, but it's not handled by this case.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling

**Justification:** The rule identifies unhandled command-line arguments, which is a form of input validation/error handling. While not a direct security control, robust handling of input parameters is a prerequisite for secure software.

**Caveat:** This is a general software quality rule, not a specific security requirement.

### shellcheck:SC2213:rank_5:SR 5.2 RE 1

- Source rule: `SC2213` — getopts specified -n, but it's not handled by this case.
- Rank: `5`
- IEC target: `SR 5.2 RE 1` — Deny by default, allow by exception
- Relative score: `0.799766`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Robustness and predictable behavior

**Justification:** The rule ensures that all defined options are handled, which aligns with the principle of explicit control and avoiding undefined behavior, loosely related to deny-by-default logic in command processing.

**Caveat:** This is a code quality/correctness rule rather than a network traffic control rule.

### shellcheck:SC2214:rank_5:SR 3.7

- Source rule: `SC2214` — This case is not specified by getopts.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.703839`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and input validation

**Justification:** The rule identifies a logic error in command-line argument parsing. While this is a form of error handling, it is a functional bug rather than a security-focused error handling mechanism as described in SR 3.7.

**Caveat:** The rule is a general code quality check; its relevance to security depends on whether the script handles sensitive inputs or system configurations.

### shellcheck:SC2215:rank_1:SR 3.7

- Source rule: `SC2215` — This flag is used as a command name. Bad line break or missing [ .. ]?
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling

**Justification:** The rule catches syntax errors that could lead to unexpected script behavior. While this improves reliability, it is not specifically an error handling mechanism for security-critical conditions.

**Caveat:** The rule is primarily a syntax/logic check.

### shellcheck:SC2215:rank_3:SR 3.5

- Source rule: `SC2215` — This flag is used as a command name. Bad line break or missing [ .. ]?
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.908058`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies syntax errors that could lead to unintended command execution. While this is a form of input validation (ensuring the shell interprets commands as intended), it is a general software quality issue rather than a specific security control for industrial process inputs.

**Caveat:** The rule is primarily a bug-finding tool for shell scripts, not a security-specific input validation mechanism.

### shellcheck:SC2216:rank_1:SR 3.7

- Source rule: `SC2216` — Piping to rm, a command that doesn't read stdin. Wrong command or missing xargs?
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and command execution

**Justification:** SC2216 identifies incorrect piping logic (e.g., using | instead of ||). While this relates to error handling in scripts, it is a general programming correctness issue rather than the security-focused error handling required by SR 3.7, which aims to prevent information leakage during system errors.

**Caveat:** The rule helps prevent logic errors that could lead to unexpected system states, which is tangentially related to system reliability.

### shellcheck:SC2220:rank_1:SR 3.7

- Source rule: `SC2220` — Invalid flags are not handled. Add a *) case.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `direct`

**Security objective:** Error handling

**Justification:** The rule enforces proper handling of unexpected input (invalid flags), which is a fundamental aspect of robust error handling as required by SR 3.7.

**Caveat:** While the rule improves robustness, the specific requirement SR 3.7 also emphasizes preventing information disclosure, which this rule only partially addresses by suggesting a generic usage message.

### shellcheck:SC2220:rank_2:SR 1.11

- Source rule: `SC2220` — Invalid flags are not handled. Add a *) case.
- Rank: `2`
- IEC target: `SR 1.11` — Unsuccessful login attempts
- Relative score: `0.870071`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Input validation and error handling

**Justification:** The rule ensures that invalid flags are handled, which is a form of input validation. While SR 1.11 focuses on limiting invalid access attempts (login), robust input handling in scripts is a foundational practice for preventing unexpected behavior that could lead to security vulnerabilities.

**Caveat:** The rule is primarily about script correctness and robustness rather than specifically enforcing login attempt limits.

### shellcheck:SC2221:rank_1:SR 3.2 RE 1

- Source rule: `SC2221` — This pattern always overrides a later one.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Input validation and logic correctness

**Justification:** The rule identifies logic errors in pattern matching. While this improves code reliability, it is not directly related to malicious code protection mechanisms at entry/exit points as defined in SR 3.2.

**Caveat:** The relationship is weak; the rule prevents logic bugs, not malicious code injection.

### shellcheck:SC2221:rank_2:SR 3.5

- Source rule: `SC2221` — This pattern always overrides a later one.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.999882`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Direct`
- Directness: `Medium`

**Security objective:** Input validation

**Justification:** The rule identifies flawed logic in input processing (case statements). Ensuring that input patterns are correctly defined and not overridden is a fundamental aspect of validating the syntax and content of inputs.

**Caveat:** The rule is a static analysis check for code correctness, which supports the broader requirement of input validation.

### shellcheck:SC2221:rank_3:SR 3.7

- Source rule: `SC2221` — This pattern always overrides a later one.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.907136`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Error handling

**Justification:** The rule identifies logic errors in case statements. While this is a form of error handling in code, it does not directly address the security-sensitive error handling requirements of SR 3.7, which focuses on preventing information leakage during runtime errors.

**Caveat:** The rule is about code logic, not the security implications of error messages.

### shellcheck:SC2223:rank_1:SR 3.7

- Source rule: `SC2223` — This default assignment may cause DoS due to globbing. Quote it.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Resource availability and denial of service prevention

**Justification:** The rule prevents a potential DoS condition caused by globbing. While SR 3.7 focuses on error handling, preventing resource exhaustion is a component of system robustness and availability, which is often linked to error handling and system stability.

**Caveat:** The rule is primarily a coding best practice for performance/stability rather than a direct error-handling mechanism as described in SR 3.7.

### shellcheck:SC2223:rank_3:SR 3.5

- Source rule: `SC2223` — This default assignment may cause DoS due to globbing. Quote it.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.783327`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Prevent unintended command interpretation and resource exhaustion via input validation.

**Justification:** The rule prevents glob expansion of unquoted variables, which is a form of input validation that ensures data is treated as literal values rather than executable patterns, directly aligning with the requirement to validate input syntax to prevent unintended interpretation.

**Caveat:** The rule is specific to shell scripting, while the SR is broader.

### shellcheck:SC2223:rank_8:SR 2.4

- Source rule: `SC2223` — This default assignment may cause DoS due to globbing. Quote it.
- Rank: `8`
- IEC target: `SR 2.4` — Mobile code
- Relative score: `0.752896`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Availability

**Justification:** The rule prevents a potential Denial of Service (DoS) caused by globbing in shell scripts. While SR 2.4 focuses on mobile code, preventing DoS is a general security objective that could be considered part of the broader system integrity and availability requirements, though the link to mobile code specifically is weak.

**Caveat:** The rule addresses general script robustness rather than mobile code specifically.

### shellcheck:SC2224:rank_1:SR 3.2 RE 1

- Source rule: `SC2224` — This mv has no destination. Check the arguments.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Integrity

**Justification:** The rule identifies a logic error in file movement. While this improves script reliability, it does not directly relate to malicious code protection at entry/exit points, unless the script is specifically handling external data at a boundary.

**Caveat:** The rule is a general coding error check, not a security-specific control.

### shellcheck:SC2225:rank_2:SR 7.3

- Source rule: `SC2225` — This cp has no destination. Check the arguments.
- Rank: `2`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.877122`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Control system backup

**Justification:** While the rule identifies a syntax error in a file copy command, which is a mechanism used in backups, the rule itself is a generic coding error check, not a security control for backup integrity.

**Caveat:** The rule helps ensure that file operations are syntactically correct, which is a prerequisite for reliable backups.

### shellcheck:SC2225:rank_3:SR 3.7

- Source rule: `SC2225` — This cp has no destination. Check the arguments.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.748959`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule identifies a syntax error that could lead to unexpected script behavior or error conditions, which relates to the broader topic of error handling, though it is not a security-specific error handling mechanism.

**Caveat:** The rule is a static analysis check for code correctness, not a design requirement for secure error handling.

### shellcheck:SC2229:rank_2:SR 3.5

- Source rule: `SC2229` — This does not read foo. Remove $/${} for that, or use ${var?} to quiet.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.928434`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** While the rule is primarily about a logic error in variable assignment, the use of unquoted or incorrectly expanded variables in shell scripts can lead to command injection or unintended execution paths if the input is attacker-controlled. SR 3.5 requires validating input to prevent it from being interpreted as commands. The rule helps ensure that the intended variable is used, which is a prerequisite for secure input handling.

**Caveat:** The rule is a static analysis check for a common coding mistake rather than a comprehensive input validation mechanism.

### shellcheck:SC2229:rank_5:SR 3.7

- Source rule: `SC2229` — This does not read foo. Remove $/${} for that, or use ${var?} to quiet.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.809489`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule mentions that using ${var?} provides an improved runtime error message, which touches upon the quality of error handling, though the primary purpose of the rule is bug prevention rather than security-focused error reporting.

**Caveat:** The rule is primarily about functional correctness, not security-sensitive error disclosure.

### shellcheck:SC2231:rank_4:SR 3.5

- Source rule: `SC2231` — Quote expansions in this for loop glob to prevent word splitting, e.g. "${dir}"/*.txt.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.832583`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** While SC2231 is primarily about shell robustness, failing to quote variables can lead to unintended command execution if the variable content is controlled by an external source, which touches upon the principle of input validation.

**Caveat:** The rule is primarily a coding best practice rather than a dedicated security input validation mechanism.

### shellcheck:SC2238:rank_1:SR 3.7

- Source rule: `SC2238` — Redirecting to/from command name instead of file. Did you want pipes/xargs (or quote to ignore)?
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust command execution and error prevention

**Justification:** The rule prevents accidental file creation when a command was intended, which could lead to unexpected system behavior or errors. While not directly an error handling security requirement, preventing unintended command execution is a form of system robustness.

**Caveat:** The rule is primarily about developer intent rather than security-critical error handling.

### shellcheck:SC2238:rank_4:SR 3.5

- Source rule: `SC2238` — Redirecting to/from command name instead of file. Did you want pipes/xargs (or quote to ignore)?
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.761123`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command interpretation

**Justification:** The rule helps ensure that commands are executed as intended rather than treating input as a filename. This touches on the concept of preventing unintended command interpretation, which is mentioned in the rationale for SR 3.5.

**Caveat:** The rule is a static analysis check for syntax errors, not a security-focused input validation mechanism.

### shellcheck:SC2239:rank_1:SR 3.7

- Source rule: `SC2239` — Ensure the shebang uses the absolute path to the interpreter.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Ensure reliable execution environment

**Justification:** Using absolute paths in shebangs improves system reliability and predictability. While not directly related to error handling, it prevents execution errors that could lead to system instability.

**Caveat:** This is a best practice for system stability, not a direct security control for error handling.

### shellcheck:SC2239:rank_2:SR 3.5

- Source rule: `SC2239` — Ensure the shebang uses the absolute path to the interpreter.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.983772`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Ensure reliable execution environment

**Justification:** Ensuring the correct interpreter is invoked via an absolute path is a form of input validation for the execution environment, though it is more about configuration integrity than process control input validation.

**Caveat:** The rule is a configuration best practice rather than a security-focused input validation mechanism.

### shellcheck:SC2239:rank_4:SR 3.2 RE 1

- Source rule: `SC2239` — Ensure the shebang uses the absolute path to the interpreter.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.908551`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** System integrity and execution reliability

**Justification:** Ensuring absolute paths in shebangs prevents execution of unintended or malicious binaries located in the PATH, which contributes to the integrity of the execution environment, a prerequisite for malicious code protection.

**Caveat:** This is a best practice for script robustness rather than a direct malicious code protection mechanism.

### shellcheck:SC2240:rank_5:SR 3.5

- Source rule: `SC2240` — The dot command does not support arguments in sh/dash. Set them as variables.
- Rank: `5`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.843921`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell portability, the suggested fix (using variables instead of positional arguments) is a form of structured input handling. However, it does not address the security-critical validation of input content or syntax.

**Caveat:** The rule is a best practice for script reliability, not a security control for input validation.

### shellcheck:SC2241:rank_1:SR 3.7

- Source rule: `SC2241` — The exit status can only be one integer 0-255. Use stdout for other data.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and information disclosure

**Justification:** The rule encourages proper use of stdout for data instead of misusing exit codes, which relates to robust error handling. However, it is a syntax/best-practice rule rather than a security-focused error handling mechanism.

**Caveat:** The rule is primarily about language correctness, not security-sensitive error reporting.

### shellcheck:SC2242:rank_1:SR 3.7

- Source rule: `SC2242` — Can only exit with status 0-255. Other data should be written to stdout/stderr.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `indirect`

**Security objective:** Error handling and information disclosure

**Justification:** The rule enforces correct error handling by directing error messages to stderr rather than attempting to pass them via exit codes, which aligns with the requirement to handle errors without leaking information to unauthorized channels.

**Caveat:** The rule is a best practice for shell scripting, which contributes to the broader goal of robust error handling required by SR 3.7.

### shellcheck:SC2243:rank_2:SR 3.5

- Source rule: `SC2243` — Prefer explicit -n to check for output (or run command without [/[[ to check for success)
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.914382`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell syntax, using explicit checks for command output can prevent logic errors that might lead to improper handling of process control inputs. However, it is not a direct input validation mechanism.

**Caveat:** The rule is a best practice for code clarity rather than a security-focused input validation control.

### shellcheck:SC2243:rank_6:SR 3.7

- Source rule: `SC2243` — Prefer explicit -n to check for output (or run command without [/[[ to check for success)
- Rank: `6`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.801814`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and secure coding practices

**Justification:** The rule encourages explicit checking of command success versus output content, which is a best practice for robust script execution. While this contributes to overall system reliability and error handling, it is a general coding practice rather than a specific implementation of the security-focused error handling requirements in SR 3.7.

**Caveat:** The rule is a general software quality improvement; its impact on security-specific error handling is incidental.

### shellcheck:SC2244:rank_1:SR 3.5

- Source rule: `SC2244` — Prefer explicit -n to check non-empty string (or use =/-ne to check boolean/integer).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule encourages explicit string checks to avoid logical errors in shell scripts. While this improves code robustness, it is a general programming best practice rather than a direct implementation of security-focused input validation (e.g., sanitization or range checking) required by SR 3.5.

**Caveat:** The rule is primarily stylistic/correctness-oriented, though it prevents logic bugs that could lead to improper input handling.

### shellcheck:SC2245:rank_2:SR 7.3 RE 1

- Source rule: `SC2245` — -d only applies to the first expansion of this glob. Use a loop to check any/all.
- Rank: `2`
- IEC target: `SR 7.3 RE 1` — Backup verification
- Relative score: `0.978708`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Reliability of backup mechanisms

**Justification:** The rule ensures correct file handling in scripts. While script reliability is generally important for system maintenance, it is not specifically tied to the verification of backup mechanisms.

**Caveat:** The relationship is purely incidental; the rule improves code correctness but does not address the specific requirement of verifying backup reliability.

### shellcheck:SC2245:rank_4:SR 3.3

- Source rule: `SC2245` — -d only applies to the first expansion of this glob. Use a loop to check any/all.
- Rank: `4`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.805454`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Security functionality verification

**Justification:** The rule helps ensure that scripts behave as intended. If a script is part of a security function, ensuring it correctly processes all files (rather than just the first) supports the reliability of that function.

**Caveat:** The rule is a general coding best practice and not a specific security verification mechanism.

### shellcheck:SC2245:rank_5:SR 7.3

- Source rule: `SC2245` — -d only applies to the first expansion of this glob. Use a loop to check any/all.
- Rank: `5`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.774867`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Control system backup

**Justification:** If the script is used to identify files for backup, the rule ensures all files are processed. However, the rule itself is not a backup mechanism.

**Caveat:** The rule is a general-purpose coding fix, not a backup-specific control.

### shellcheck:SC2246:rank_1:SR 3.5

- Source rule: `SC2246` — This shebang specifies a directory. Ensure the interpreter is a file.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule ensures the interpreter path is a valid file, which is a form of system configuration validation. While not strictly 'input validation' of process control data, it prevents execution of malformed paths which could be exploited.

**Caveat:** The requirement focuses on industrial process control inputs, whereas this rule focuses on system configuration/execution environment integrity.

### shellcheck:SC2246:rank_6:SR 2.4 RE 1

- Source rule: `SC2246` — This shebang specifies a directory. Ensure the interpreter is a file.
- Rank: `6`
- IEC target: `SR 2.4 RE 1` — Mobile code integrity check
- Relative score: `0.700313`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** System integrity and configuration correctness

**Justification:** While the rule is a basic syntax check, ensuring the correct interpreter is invoked is a prerequisite for the integrity of the execution environment, which relates to mobile code integrity.

**Caveat:** The rule is a static syntax check, not a cryptographic integrity check as implied by the requirement.

### shellcheck:SC2247:rank_1:SR 3.5

- Source rule: `SC2247` — Flip leading $ and " if this should be a quoted substitution.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule identifies incorrect shell syntax that leads to unintended command interpretation. This directly relates to the requirement to validate input to prevent it from being unintentionally interpreted as commands.

**Caveat:** The rule is a static analysis check for syntax, which is a foundational step in input validation.

### shellcheck:SC2248:rank_1:SR 3.2 RE 1

- Source rule: `SC2248` — Problematic code:
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `defensive coding`
- Directness: `indirect`

**Security objective:** Prevention of malicious code execution

**Justification:** Quoting variables prevents word splitting and globbing, which can be exploited to execute unintended files or commands. This is a defensive coding practice that supports malicious code protection at entry points.

**Caveat:** This is a general best practice for shell scripting rather than a dedicated malicious code protection mechanism.

### shellcheck:SC2248:rank_3:SR 3.2

- Source rule: `SC2248` — Problematic code:
- Rank: `3`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.807972`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `defensive coding`
- Directness: `indirect`

**Security objective:** Prevention of malicious code execution

**Justification:** Similar to SR 3.2 RE 1, quoting variables is a defensive practice that reduces the attack surface for malicious code injection via shell expansion, supporting the broader goal of malicious code protection.

**Caveat:** This is a general coding practice, not a specific security mechanism for detecting or mitigating malicious code.

### shellcheck:SC2249:rank_2:SR 3.7

- Source rule: `SC2249` — Consider adding a default *) case, even if it just exits with error.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.848691`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `indirect`

**Security objective:** Robust error handling

**Justification:** SR 3.7 requires identifying and handling error conditions. SC2249 enforces the handling of unexpected or default cases in logic, which is a fundamental aspect of robust error handling and preventing undefined behavior.

**Caveat:** The rule is a general coding best practice; its application to security depends on whether the specific case statement handles security-sensitive logic.

### shellcheck:SC2249:rank_3:SR 5.2 RE 1

- Source rule: `SC2249` — Consider adding a default *) case, even if it just exits with error.
- Rank: `3`
- IEC target: `SR 5.2 RE 1` — Deny by default, allow by exception
- Relative score: `0.741477`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `analogous`
- Directness: `indirect`

**Security objective:** Default-deny logic

**Justification:** While SC2249 is about code logic, the principle of 'default case' is conceptually similar to 'deny by default'. However, SR 5.2 RE 1 is specifically about network traffic, not general code branching.

**Caveat:** The analogy is conceptual rather than functional.

### shellcheck:SC2249:rank_7:SR 7.1

- Source rule: `SC2249` — Consider adding a default *) case, even if it just exits with error.
- Rank: `7`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `0.691736`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robustness and error handling

**Justification:** While the rule improves code robustness, its connection to DoS protection (SR 7.1) is tenuous. A default case might prevent unexpected behavior, but it does not specifically address the capability to operate in a degraded mode during a DoS event.

**Caveat:** The rule is a general coding best practice rather than a specific security control for DoS.

### shellcheck:SC2250:rank_3:SR 3.5

- Source rule: `SC2250` — Prefer putting braces around variable references even when not strictly required.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.935247`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code correctness and variable expansion

**Justification:** The rule prevents variable expansion errors. While this is a form of input/data handling, it is not related to the security-critical validation of external inputs or process control inputs required by SR 3.5.

**Caveat:** The rule is a general coding best practice rather than a security-focused input validation control.

### shellcheck:SC2251:rank_1:SR 3.7

- Source rule: `SC2251` — This ! is not on a condition and skips errexit. Add || exit 1 or make sure $? is checked.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Direct support`
- Directness: `Direct`

**Security objective:** Robust error handling

**Justification:** The rule identifies a logic error where a command failure is ignored due to the misuse of '!', which directly undermines the system's ability to handle errors correctly as required by SR 3.7.

**Caveat:** The rule is specific to shell scripting, whereas the SR is a general requirement.

### shellcheck:SC2251:rank_3:SR 5.2 RE 3

- Source rule: `SC2251` — This ! is not on a condition and skips errexit. Add || exit 1 or make sure $? is checked.
- Rank: `3`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `0.891293`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect support`
- Directness: `Indirect`

**Security objective:** Fail-safe operation

**Justification:** While the rule improves error handling, it is not specifically related to the 'fail close' mechanism of boundary protection systems.

**Caveat:** Only relevant if the script being checked is part of a boundary protection mechanism.

### shellcheck:SC2252:rank_1:SR 3.5

- Source rule: `SC2252` — You probably wanted && here, otherwise it's always true.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Direct support`
- Directness: `Direct`

**Security objective:** Input validation

**Justification:** The rule identifies a logical flaw in conditional checks that validate input. Correcting this logic is essential for ensuring that input validation routines function as intended.

**Caveat:** The rule is a general programming logic check, not a specific security-focused input validation library.

### shellcheck:SC2253:rank_1:SR 4.2

- Source rule: `SC2253` — Use -R to recurse, or explicitly a-r to remove read permissions.
- Rank: `1`
- IEC target: `SR 4.2` — Information persistence
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `access_control_configuration`
- Directness: `indirect`

**Security objective:** Information access control

**Justification:** The rule warns about the misuse of chmod flags, which could lead to unintended file permissions. While related to access control, it does not specifically address the purging of information upon decommissioning as required by SR 4.2.

**Caveat:** The rule helps prevent accidental permission settings, which is a component of information security, but it is not a direct implementation of the decommissioning/purging requirement.

### shellcheck:SC2254:rank_1:SR 3.5

- Source rule: `SC2254` — Quote expansions in case patterns to match literally rather than as a glob.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input_validation`
- Directness: `direct`

**Security objective:** Input validation and sanitization

**Justification:** The rule enforces quoting variables in case patterns to prevent them from being interpreted as globs. This is a form of input validation/sanitization that prevents unintended interpretation of input data, directly aligning with the requirement to prevent content from being unintentionally interpreted as commands.

**Caveat:** This is a specific implementation detail for shell scripting, but it directly addresses the security principle of preventing injection-style vulnerabilities through improper input handling.

### shellcheck:SC2254:rank_2:SR 3.2 RE 1

- Source rule: `SC2254` — Quote expansions in case patterns to match literally rather than as a glob.
- Rank: `2`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.753395`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Malicious code protection

**Justification:** The rule prevents glob expansion in case patterns, which is a form of input sanitization. While not a direct 'malicious code protection' mechanism like an antivirus, it prevents unexpected code execution paths that could be exploited.

**Caveat:** This is a coding best practice for robustness rather than a dedicated security control against malicious code.

### shellcheck:SC2255:rank_1:SR 3.5

- Source rule: `SC2255` — [ ] does not apply arithmetic evaluation. Evaluate with $((..)) for numbers, or use string comparator for strings.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `high`

**Security objective:** Input validation

**Justification:** The rule enforces correct syntax for arithmetic evaluation in shell scripts. By ensuring inputs are correctly evaluated or treated as strings, it prevents logic errors that could lead to unexpected behavior or security vulnerabilities when processing control inputs.

**Caveat:** The rule is primarily about correctness, but in the context of shell scripting, it is a fundamental aspect of input validation.

### shellcheck:SC2255:rank_2:SR 3.7

- Source rule: `SC2255` — [ ] does not apply arithmetic evaluation. Evaluate with $((..)) for numbers, or use string comparator for strings.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.889469`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** Incorrect arithmetic evaluation can lead to runtime errors. Ensuring proper evaluation helps avoid unhandled errors, but the rule itself does not address the security of error messages.

**Caveat:** The rule prevents errors but does not manage the disclosure of information during error conditions.

### shellcheck:SC2256:rank_1:SR 3.5

- Source rule: `SC2256` — This translated string is the name of a variable. Flip leading $ and " if this should be a quoted substitution.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Preventing unintended interpretation of input data

**Justification:** The rule addresses potential confusion between localized strings and variable substitution, which is a form of syntax handling. While not a direct security validation of external input, it relates to the broader goal of ensuring that data (strings) are interpreted as intended by the developer, which aligns with the spirit of preventing malformed input interpretation.

**Caveat:** This is a coding best practice for correctness rather than a direct security control against malicious input.

### shellcheck:SC2258:rank_1:SR 3.5

- Source rule: `SC2258` — The trailing comma is part of the value, not a separator. Delete or quote it.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule identifies malformed input syntax (commas in a loop list). While this is a syntax error, it relates to the broader category of ensuring input is parsed as intended, which is a foundational aspect of input validation.

**Caveat:** This is a static analysis rule for shell syntax, not a security-specific input validation check.

### shellcheck:SC2259:rank_2:SR 3.7

- Source rule: `SC2259` — This redirection overrides piped input. To use both, merge or pass filenames.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.959161`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule identifies a situation where a command might fail to process intended input due to redirection conflicts. While this is an error condition, it is a functional scripting error rather than a security-relevant error handling mechanism.

**Caveat:** The rule is a linter warning for shell scripts, not a security-focused error handling implementation.

### shellcheck:SC2259:rank_3:SR 3.5

- Source rule: `SC2259` — This redirection overrides piped input. To use both, merge or pass filenames.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.94899`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and data integrity

**Justification:** The rule addresses a logic error where input streams are incorrectly handled, potentially leading to missing data. While not a direct security validation of input content, ensuring that all intended input is correctly processed is a prerequisite for reliable input validation.

**Caveat:** This is a functional correctness issue rather than a security-focused input validation check.

### shellcheck:SC2261:rank_2:SR 3.7

- Source rule: `SC2261` — Multiple redirections compete for stdout. Use cat, tee, or pass filenames instead.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.846818`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and system robustness

**Justification:** While the rule is a syntax correction, improper handling of file descriptors and redirections can lead to unexpected system behavior or error conditions, which relates to the broader goal of robust error handling.

**Caveat:** The rule is primarily a functional correctness issue, not a security-specific error handling mechanism.

### shellcheck:SC2262:rank_1:SR 3.3

- Source rule: `SC2262` — This alias can't be defined and used in the same parsing unit. Use a function instead.
- Rank: `1`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Security functionality verification

**Justification:** While the rule improves code reliability, it is a general programming best practice. It only relates to SR 3.3 if the alias/function logic is part of a security-critical script that requires verification.

**Caveat:** The rule is a general coding standard and not specifically a security control.

### shellcheck:SC2265:rank_3:SR 3.5

- Source rule: `SC2265` — Use && for logical AND. Single & will background and return true.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.701258`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Correct logical operator usage in shell scripts

**Justification:** The rule ensures that conditional checks are executed correctly. If a security-critical check (e.g., checking user permissions) is bypassed due to a syntax error (backgrounding), it could lead to improper input validation or authorization bypass.

**Caveat:** The rule is a general syntax fix, not a specific input validation mechanism, but it prevents logic bypasses that could impact security.

### shellcheck:SC2266:rank_1:SR 3.5

- Source rule: `SC2266` — Use || for logical OR. Single | will pipe.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and logical correctness

**Justification:** While the rule is primarily a syntax fix for shell logic, it directly affects how input parameters (like --verbose) are evaluated. If the logic fails due to a syntax error, the system may fail to validate or process inputs correctly, which is tangentially related to input validation.

**Caveat:** The rule is a general coding best practice rather than a specific security control for input validation.

### shellcheck:SC2267:rank_2:SR 3.5

- Source rule: `SC2267` — GNU xargs -i is deprecated in favor of -I{}
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.957867`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule encourages using explicit replacement strings in xargs, which can help prevent unintended command interpretation. While this aligns with the goal of preventing command injection mentioned in the SR 3.5 rationale, the rule itself is primarily a POSIX compliance/best practice issue rather than a direct security control.

**Caveat:** The rule is a coding best practice for portability and clarity, not a direct security validation mechanism.

### shellcheck:SC2268:rank_7:SR 3.5

- Source rule: `SC2268` — Avoid x-prefix in comparisons as it no longer serves a purpose.
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.843861`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Ensure input syntax is handled correctly to prevent unexpected behavior.

**Justification:** The rule addresses potential shell interpretation issues with specific characters. While this is a form of input handling, it is primarily a coding style/portability fix rather than a security-focused input validation mechanism as defined in SR 3.5.

**Caveat:** The rule is more about shell portability than security, though improper input handling can lead to command injection in shell scripts.

### shellcheck:SC2270:rank_4:SR 3.5

- Source rule: `SC2270` — To assign positional parameters, use set -- first second .. (or use [ ] to compare).
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.878088`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about syntax, the problematic code shows an attempt to interpret a variable as a command or assignment, which touches on the broader concept of input handling. However, it is a stretch to call this 'input validation' in the context of industrial process control.

**Caveat:** The rule is a static analysis check for shell scripting best practices, not a security-focused input validation mechanism.

### shellcheck:SC2270:rank_8:SR 3.7

- Source rule: `SC2270` — To assign positional parameters, use set -- first second .. (or use [ ] to compare).
- Rank: `8`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.745995`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** While the rule fixes syntax that could lead to unexpected script behavior (a form of error), it is a general coding best practice rather than a security-focused error handling mechanism as described in SR 3.7.

**Caveat:** The rule prevents logic errors, but does not address the security implications of error message disclosure.

### shellcheck:SC2271:rank_2:SR 3.5

- Source rule: `SC2271` — For indirection, use arrays, declare "var$n=value", or (for sh) read/eval
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.913957`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule prevents unsafe dynamic variable creation (often involving shell expansion/evaluation), which is a form of input validation and sanitization to prevent command injection or unintended code execution.

**Caveat:** The rule is a best practice for shell scripting, but it directly maps to the requirement of screening inputs passed to interpreters.

### shellcheck:SC2271:rank_5:SR 3.8

- Source rule: `SC2271` — For indirection, use arrays, declare "var$n=value", or (for sh) read/eval
- Rank: `5`
- IEC target: `SR 3.8` — Session integrity
- Relative score: `0.7317`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `session integrity`
- Directness: `indirect`

**Security objective:** Session integrity

**Justification:** While the rule improves code robustness, it is only tangentially related to session integrity if the dynamic variable assignment were used to manipulate session identifiers.

**Caveat:** The relationship is highly speculative and context-dependent.

### shellcheck:SC2272:rank_1:SR 3.5

- Source rule: `SC2272` — Command name contains ==. For comparison, use [ "$var" = value ].
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command execution safety

**Justification:** The rule identifies incorrect syntax that could lead to unintended command execution if the shell interprets the string as a command rather than a comparison. This relates to the broader goal of ensuring inputs are not misinterpreted as commands.

**Caveat:** The rule is primarily a syntax correction rather than a security-focused input validation check.

### shellcheck:SC2273:rank_1:SR 3.2 RE 1

- Source rule: `SC2273` — Sequence of ===s found. Merge conflict or intended as a commented border?
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `code_integrity_to_security`
- Directness: `indirect`

**Security objective:** Code integrity and configuration management

**Justification:** Unresolved merge conflicts (the primary issue identified by the rule) can lead to broken code or unintended logic, which could theoretically impact the reliability of security mechanisms. However, this is a general software quality issue, not a specific malicious code protection mechanism.

**Caveat:** The rule is primarily a developer productivity/quality tool, not a security control.

### shellcheck:SC2273:rank_3:SR 3.7

- Source rule: `SC2273` — Sequence of ===s found. Merge conflict or intended as a commented border?
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.83627`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `code_integrity_to_security`
- Directness: `indirect`

**Security objective:** Error handling and code quality

**Justification:** Unresolved merge conflicts can lead to unexpected application behavior or crashes, which are types of error conditions. However, the rule does not specifically address the security-sensitive aspects of error handling (e.g., information leakage).

**Caveat:** The rule is a general code quality check, not a security-specific error handling mechanism.

### shellcheck:SC2275:rank_1:SR 3.5

- Source rule: `SC2275` — Command name starts with =. Bad line break?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntactic_to_functional`
- Directness: `indirect`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule identifies malformed syntax that could lead to unintended command execution if the input is interpreted. While primarily a syntax error, it touches on the principle of ensuring inputs are not misinterpreted as commands, which aligns with the rationale of SR 3.5.

**Caveat:** The rule is primarily a linter for developer error rather than a security control against malicious input.

### shellcheck:SC2276:rank_1:SR 3.5

- Source rule: `SC2276` — This is interpreted as a command name containing =. Bad assignment or comparison?
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntactic_to_functional`
- Directness: `indirect`

**Security objective:** Input validation and syntax correctness

**Justification:** Similar to SC2275, this rule identifies ambiguous syntax that could be misinterpreted by an interpreter. Preventing unintended command execution is a core aspect of input validation as described in the rationale for SR 3.5.

**Caveat:** The rule is a static analysis check for developer mistakes, not a runtime security validation mechanism.

### shellcheck:SC2277:rank_2:SR 3.5

- Source rule: `SC2277` — Use BASH_ARGV0 to assign to $0 in bash (or use [ ] to compare).
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.954143`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax correction, improper handling of variables or command arguments can lead to injection vulnerabilities. However, this specific rule is about shell variable assignment syntax, not input validation of external data.

**Caveat:** The rule is a linter check for syntax, not a security-focused input validation mechanism.

### shellcheck:SC2281:rank_1:SR 3.5

- Source rule: `SC2281` — Don't use $/${} on the left side of assignments.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule prevents incorrect shell syntax that could lead to unintended command execution or logic errors. While not a direct input validation mechanism for industrial process data, it aligns with the principle of preventing malformed input from being interpreted as commands.

**Caveat:** The rule is primarily a syntax correction rather than a security-focused input validation mechanism.

### shellcheck:SC2283:rank_1:SR 3.5

- Source rule: `SC2283` — Use [ ] to compare values, or remove spaces around = to assign (or quote '=' if literal).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule prevents ambiguous shell syntax that could lead to unintended command execution or logic errors, which aligns with the requirement to validate input to prevent it from being unintentionally interpreted as commands.

**Caveat:** While the rule is primarily a syntax check, it directly mitigates the risk of command injection, which is explicitly mentioned in the rationale for SR 3.5.

### shellcheck:SC2286:rank_1:SR 3.5

- Source rule: `SC2286` — This empty string is interpreted as a command name. Double check syntax (or use 'true' as a no-op).
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_error_vs_input_validation`
- Directness: `indirect`

**Security objective:** Command execution safety

**Justification:** The rule identifies a syntax error where an empty string is interpreted as a command. This is relevant to SR 3.5 because improper handling of input (e.g., empty strings or unexpected characters) can lead to unintended command execution or command injection.

**Caveat:** The rule is primarily a syntax check, but it prevents a class of errors that could lead to unexpected command execution.

### shellcheck:SC2286:rank_4:SR 3.7

- Source rule: `SC2286` — This empty string is interpreted as a command name. Double check syntax (or use 'true' as a no-op).
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.840102`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and robustness

**Justification:** The rule identifies a syntax error that could lead to unexpected script behavior or failure. While this relates to error handling, it is a general coding quality issue rather than a specific security-focused error handling mechanism as described in SR 3.7.

**Caveat:** The rule is a static analysis check for syntax, whereas SR 3.7 focuses on the design of error messages and handling logic to prevent information disclosure.

### shellcheck:SC2287:rank_3:SR 3.5

- Source rule: `SC2287` — This is interpreted as a command name ending with '/'. Double check syntax.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.775391`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** The rule identifies a syntax error where a path is misinterpreted as a command. While this is a static syntax check, it touches on the concept of ensuring inputs are not misinterpreted, which is a core principle of input validation.

**Caveat:** This is a developer-level syntax check, not a robust security input validation mechanism.

### shellcheck:SC2288:rank_1:SR 3.5

- Source rule: `SC2288` — This is interpreted as a command name ending with apostrophe. Double check syntax.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule identifies syntax errors that could lead to unintended command execution. While the rule is primarily about fixing syntax, the rationale for SR 3.5 explicitly mentions preventing content from being unintentionally interpreted as commands, which aligns with the risk of malformed input.

**Caveat:** The rule is a static syntax check, whereas SR 3.5 is a broader security requirement for input validation against malicious intent.

### shellcheck:SC2289:rank_1:SR 3.5

- Source rule: `SC2289` — This is interpreted as a command name containing a linefeed. Double check syntax.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `indirect`

**Security objective:** Input validation and sanitization

**Justification:** SC2289 detects malformed input (e.g., unexpected characters in command names) that could lead to unintended execution. This aligns with the requirement to validate input to prevent it from being interpreted as commands, which is explicitly mentioned in the SR 3.5 rationale.

**Caveat:** The rule is a static analysis check for syntax, which is a subset of the broader input validation requirements.

### shellcheck:SC2290:rank_4:SR 3.5

- Source rule: `SC2290` — Remove spaces around = to assign.
- Rank: `4`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.739391`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily a syntax check, ensuring correct variable assignment prevents unintended behavior in scripts, which is a very distant form of ensuring the script behaves as intended, but it does not constitute input validation of external data.

**Caveat:** The rule is a static syntax check for the developer, not a runtime validation of external inputs.

### shellcheck:SC2291:rank_1:SR 3.5

- Source rule: `SC2291` — Quote repeated spaces to avoid them collapsing into one.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect_input_handling`
- Directness: `weak`

**Security objective:** Input validation and formatting

**Justification:** While the rule is primarily about shell output formatting, improper handling of spaces in inputs can lead to command injection or misinterpretation of arguments in shell scripts, which relates to the broader goal of input validation.

**Caveat:** The rule is primarily a cosmetic/formatting issue rather than a security-critical input validation check.

### shellcheck:SC2292:rank_1:SR 7.1

- Source rule: `SC2292` — Prefer [[ ]] over [ ] for tests in Bash/Ksh.
- Rank: `1`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robustness and error handling

**Justification:** Using [[ ]] is safer and more robust than [ ], which can prevent certain shell injection or logic errors that might lead to unexpected behavior during a DoS event, though the link is weak.

**Caveat:** The rule is primarily a best practice for code quality rather than a specific DoS mitigation strategy.

### shellcheck:SC2292:rank_2:SR 3.5

- Source rule: `SC2292` — Prefer [[ ]] over [ ] for tests in Bash/Ksh.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.903518`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and safe execution

**Justification:** The rule promotes safer test constructs that avoid word splitting and globbing, which can be a form of input validation/sanitization when processing variables in shell scripts.

**Caveat:** This is a coding standard improvement rather than a direct implementation of input validation logic for industrial process control inputs.

### shellcheck:SC2293:rank_1:SR 3.5

- Source rule: `SC2293` — When eval'ing @Q-quoted words, use * rather than @ as the index.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Prevent command injection via improper evaluation of input strings.

**Justification:** The rule addresses the unsafe use of 'eval' with array expansion, which is a classic vector for command injection. SR 3.5 explicitly requires validating inputs passed to interpreters to prevent them from being unintentionally interpreted as commands.

**Caveat:** None

### shellcheck:SC2293:rank_4:SR 3.2 RE 1

- Source rule: `SC2293` — When eval'ing @Q-quoted words, use * rather than @ as the index.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.752256`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Malicious code protection`
- Directness: `Indirect`

**Security objective:** Preventing malicious code execution.

**Justification:** While the rule prevents command injection (a form of malicious code execution), SR 3.2 RE 1 is typically focused on mechanisms like antivirus or signature-based detection at entry/exit points, rather than secure coding practices for internal script evaluation.

**Caveat:** The rule is a secure coding practice, whereas the requirement is often interpreted as a system-level mechanism.

### shellcheck:SC2294:rank_2:SR 3.5

- Source rule: `SC2294` — eval negates the benefit of arrays. Drop eval to preserve whitespace/symbols (or eval as string).
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.751155`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `mitigation`
- Directness: `direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule prevents improper use of 'eval' which is a classic source of command injection vulnerabilities. This directly supports SR 3.5, which requires validating inputs to prevent them from being unintentionally interpreted as commands.

**Caveat:** The rule is specific to shell scripting, while the SR is a general requirement for control systems.

### shellcheck:SC2294:rank_3:SR 3.7

- Source rule: `SC2294` — eval negates the benefit of arrays. Drop eval to preserve whitespace/symbols (or eval as string).
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.703803`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `indirect`

**Security objective:** Error handling and secure coding

**Justification:** While the rule improves code robustness, it is not primarily an error handling mechanism. The connection to SR 3.7 is weak as the rule focuses on preventing injection rather than managing error conditions.

**Caveat:** None

### shellcheck:SC2295:rank_2:SR 3.5

- Source rule: `SC2295` — Expansions inside ${..} need to be quoted separately, otherwise they will match as a pattern.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.973951`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Input validation

**Justification:** The rule prevents unintended pattern interpretation of input variables, which is a form of input validation to ensure data is treated as literal content rather than executable patterns.

**Caveat:** This is a specific instance of input handling rather than a general input validation framework.

### shellcheck:SC2296:rank_1:SR 3.5

- Source rule: `SC2296` — Parameter expansions can't start with {. Double check syntax.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule identifies syntax errors in parameter expansion, which is a form of input validation. While SR 3.5 focuses on security-critical inputs, ensuring correct syntax in scripts prevents unexpected behavior that could be exploited.

**Caveat:** The rule is primarily a code quality/syntax check rather than a security-focused input validation mechanism.

### shellcheck:SC2296:rank_9:SR 3.7

- Source rule: `SC2296` — Parameter expansions can't start with {. Double check syntax.
- Rank: `9`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.72754`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `syntax_error_vs_error_handling`
- Directness: `indirect`

**Security objective:** Code correctness and error handling

**Justification:** While SC2296 is a syntax check, ensuring correct syntax prevents runtime errors that could lead to unexpected behavior or information disclosure if error messages are poorly handled.

**Caveat:** The relationship is very weak as the rule is purely syntactic.

### shellcheck:SC2297:rank_1:SR 3.5

- Source rule: `SC2297` — Double quotes must be outside ${}: ${"invalid"} vs "${valid}".
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Input Sanitization`
- Directness: `Indirect`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule enforces correct shell syntax for parameter expansion. While primarily a code quality issue, incorrect syntax in shell scripts can lead to unexpected behavior or command injection vulnerabilities if user-controlled input is involved, which aligns with the goal of SR 3.5 to validate input syntax.

**Caveat:** The rule is a general syntax check and does not specifically target security-critical input validation as described in the IEC 62443-3-3 requirement.

### shellcheck:SC2298:rank_2:SR 3.7

- Source rule: `SC2298` — ${$x} is invalid. For expansion, use ${x}. For indirection, use arrays, ${!x} or (for sh) eval.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.876589`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and robust code execution

**Justification:** The rule identifies syntax errors in shell scripts that could lead to unexpected script behavior or crashes. While this relates to error handling, it is a general software quality issue rather than a specific security control for handling error conditions in a way that prevents information disclosure.

**Caveat:** The rule addresses syntax errors, not the handling of runtime error conditions or the secure reporting of such errors.

### shellcheck:SC2298:rank_3:SR 3.5

- Source rule: `SC2298` — ${$x} is invalid. For expansion, use ${x}. For indirection, use arrays, ${!x} or (for sh) eval.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.868264`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule identifies invalid shell parameter expansion syntax. While this is a form of syntax validation, it is a language-level correctness check rather than a security-focused input validation mechanism designed to prevent injection or malicious input processing.

**Caveat:** The rule is a static syntax check, not a security-oriented input validation filter.

### shellcheck:SC2300:rank_7:SR 3.5

- Source rule: `SC2300` — Parameter expansion can't be applied to command substitutions. Use temporary variables.
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.817566`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and code robustness

**Justification:** While SC2300 is primarily a syntax error, ensuring code is syntactically correct and uses variables properly is a prerequisite for robust input handling. However, it does not directly address the security validation of external inputs as required by SR 3.5.

**Caveat:** The rule is a linter error, not a security validation check.

### shellcheck:SC2301:rank_1:SR 3.5

- Source rule: `SC2301` — Parameter expansion starts with unexpected quotes. Double check syntax.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `input_validation`
- Directness: `indirect`

**Security objective:** Input validation and syntax correctness

**Justification:** While the rule enforces correct syntax for parameter expansion, it is a static analysis check for language-specific syntax rather than a security-focused input validation mechanism for industrial process control inputs.

**Caveat:** The rule is a general code quality check, not a security-specific input validation control.

### shellcheck:SC2302:rank_1:SR 3.5

- Source rule: `SC2302` — This loops over values. To loop over keys, use "${!array[@]}".
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies a logic error where array values are incorrectly used as keys. While this is primarily a bug, it relates to how data is processed and accessed, which is a component of robust input handling.

**Caveat:** This is a code logic error rather than a security-focused input validation check against external untrusted input.

### shellcheck:SC2303:rank_1:SR 3.5

- Source rule: `SC2303` — i is an array value, not a key. Use directly or loop over keys instead.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and correct data handling

**Justification:** The rule identifies a misuse of data (treating a value as a key), which is a form of incorrect data handling. While not direct input validation, ensuring data is used in the correct context is a prerequisite for robust software that avoids unexpected behavior.

**Caveat:** The rule is primarily a code quality/logic check rather than a security-focused input validation check.

### shellcheck:SC2304:rank_4:SR 3.7

- Source rule: `SC2304` — must be escaped to multiply: \. Modern $((x * y)) avoids this issue.
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.84435`
- Gemini verdict: **MAYBE**
- Confidence: `4/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and robustness

**Justification:** While the rule prevents a runtime error, it is a general coding best practice rather than a security-focused error handling mechanism designed to prevent information disclosure or exploitation.

**Caveat:** The rule prevents an error that could cause a script to fail, which is tangentially related to system reliability, but not specifically to the security-sensitive error handling described in SR 3.7.

### shellcheck:SC2304:rank_9:SR 3.5

- Source rule: `SC2304` — must be escaped to multiply: \. Modern $((x * y)) avoids this issue.
- Rank: `9`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.787788`
- Gemini verdict: **YES**
- Confidence: `3/5`
- Relation type: `input validation`
- Directness: `indirect`

**Security objective:** Preventing unintended command interpretation

**Justification:** The rule prevents shell globbing from interfering with command arguments, which aligns with the objective of ensuring inputs are not misinterpreted by the system.

**Caveat:** The rule is primarily a syntax/correctness issue, but it touches on the security principle of preventing unintended command execution.

### shellcheck:SC2305:rank_1:SR 3.5

- Source rule: `SC2305` — Quote regex argument to expr to avoid it expanding as a glob.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `input validation`
- Directness: `direct`

**Security objective:** Preventing injection and unintended interpretation

**Justification:** The rule explicitly addresses the need to quote regex arguments to prevent them from being treated as globs, which is a form of input sanitization/validation to ensure the command behaves as intended.

**Caveat:** The rule is a specific instance of ensuring input is treated as data rather than executable shell patterns.

### shellcheck:SC2306:rank_1:SR 3.2 RE 1

- Source rule: `SC2306` — Escape glob characters in arguments to expr to avoid pathname expansion.
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `malicious code protection`
- Directness: `indirect`

**Security objective:** Preventing unintended command execution

**Justification:** While the rule prevents shell expansion errors, it is a stretch to classify this as 'malicious code protection' at entry/exit points, though preventing unintended shell behavior is a defensive coding practice.

**Caveat:** This is a low-level syntax fix rather than a robust security mechanism for malicious code protection.

### shellcheck:SC2306:rank_5:SR 3.7

- Source rule: `SC2306` — Escape glob characters in arguments to expr to avoid pathname expansion.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.759436`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and secure coding

**Justification:** While the rule is about shell syntax, improper handling of shell commands can lead to unexpected behavior or errors. SR 3.7 requires handling errors in a way that does not expose exploitable information.

**Caveat:** The rule is primarily about functional correctness rather than security-sensitive error handling.

### shellcheck:SC2306:rank_7:SR 3.5

- Source rule: `SC2306` — Escape glob characters in arguments to expr to avoid pathname expansion.
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.74374`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Direct support`
- Directness: `Direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule prevents shell pathname expansion from interfering with command arguments, which aligns with the requirement to ensure inputs passed to interpreters are not unintentionally interpreted as commands.

**Caveat:** This is a specific instance of input validation for shell scripts.

### shellcheck:SC2307:rank_1:SR 3.5

- Source rule: `SC2307` — 'expr' expects 3+ arguments but sees 1. Make sure each operator/operand is a separate argument, and escape <>&|.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Direct support`
- Directness: `Direct`

**Security objective:** Input validation and command injection prevention

**Justification:** The rule ensures that shell metacharacters are properly escaped when passed to an interpreter, directly preventing unintended command execution or misinterpretation of input, which is a core aspect of SR 3.5.

**Caveat:** This is a specific instance of input validation for shell scripts.

### shellcheck:SC2307:rank_7:SR 3.7

- Source rule: `SC2307` — 'expr' expects 3+ arguments but sees 1. Make sure each operator/operand is a separate argument, and escape <>&|.
- Rank: `7`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.720905`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and robust input processing

**Justification:** The rule identifies syntax errors in shell expressions that could lead to unexpected script behavior or crashes. While this relates to 'error handling' in a broad sense, SR 3.7 specifically focuses on preventing the disclosure of sensitive information during error conditions, which this rule does not directly address.

**Caveat:** The rule improves code robustness, which is a prerequisite for secure error handling, but it does not specifically address the information disclosure aspect of SR 3.7.

### shellcheck:SC2308:rank_1:SR 3.5

- Source rule: `SC2308` — expr length has unspecified results. Prefer ${#var}.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `medium`

**Security objective:** Input validation and robust processing

**Justification:** The rule encourages using portable, standard shell parameter expansions instead of non-standard 'expr' commands. This improves the reliability of input processing. While SR 3.5 focuses on validating input syntax to prevent injection or malformed data, using standard, well-defined language features is a best practice that reduces the likelihood of unexpected behavior when processing inputs.

**Caveat:** The rule is primarily about portability and code quality rather than explicit security validation of untrusted input.

### shellcheck:SC2309:rank_1:SR 3.7

- Source rule: `SC2309` — -eq treats this as a variable. Use = to compare as string (or expand explicitly with $var)
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and error handling

**Justification:** The rule prevents logic errors caused by incorrect operator usage. While primarily a bug-fix, it relates to input handling, which is a prerequisite for robust error handling as described in SR 3.7.

**Caveat:** The rule is a general coding best practice rather than a specific security control for error handling.

### shellcheck:SC2309:rank_2:SR 3.5

- Source rule: `SC2309` — -eq treats this as a variable. Use = to compare as string (or expand explicitly with $var)
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.924391`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `moderate`

**Security objective:** Input validation

**Justification:** The rule identifies a case where input is incorrectly processed due to type confusion (treating a string as a number). This is a form of input validation failure where the system fails to correctly interpret the provided input.

**Caveat:** The rule is a static analysis check for code correctness, which serves as a foundational layer for the security requirement of input validation.

### shellcheck:SC2310:rank_1:SR 7.3 RE 1

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `1`
- IEC target: `SR 7.3 RE 1` — Backup verification
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `enforcement`
- Directness: `indirect`

**Security objective:** Backup reliability

**Justification:** The rule identifies a logic error where a backup process might fail silently due to shell configuration, directly impacting the reliability of the backup mechanism.

**Caveat:** This is a coding-level check that supports the requirement by ensuring the implementation of the backup mechanism is robust.

### shellcheck:SC2310:rank_2:SR 5.2 RE 3

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `2`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `0.954018`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Fail close

**Justification:** While the rule prevents silent failures in scripts, 'fail close' refers to boundary protection mechanisms. The rule is too generic to be specifically mapped to boundary protection failure handling.

**Caveat:** The rule improves general script reliability, which is a prerequisite for any fail-safe mechanism, but it is not specific to boundary protection.

### shellcheck:SC2310:rank_3:SR 7.3

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `3`
- IEC target: `SR 7.3` — Control system backup
- Relative score: `0.952478`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `enforcement`
- Directness: `indirect`

**Security objective:** Control system backup

**Justification:** The rule ensures that backup scripts do not fail silently, which is essential for the 'ability to conduct backups' requirement in SR 7.3.

**Caveat:** This rule helps ensure the integrity of the backup process implementation.

### shellcheck:SC2310:rank_4:SR 7.3 RE 2

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `4`
- IEC target: `SR 7.3 RE 2` — Backup automation
- Relative score: `0.868397`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Supportive`
- Directness: `Direct`

**Security objective:** Reliability and integrity of automated backup processes

**Justification:** The rule ensures that backup scripts do not silently fail due to suppressed error handling, which is critical for the reliability of automated backup functions required by SR 7.3 RE 2.

**Caveat:** The rule is specific to shell scripting environments and does not cover all possible backup automation technologies.

### shellcheck:SC2310:rank_6:SR 2.10

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `6`
- IEC target: `SR 2.10` — Response to audit processing failures
- Relative score: `0.728253`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Indirect`

**Security objective:** Response to audit processing failures

**Justification:** While the rule improves error handling, it is not specifically related to audit processing or the failure of audit mechanisms.

**Caveat:** Only relevant if the script in question is part of the audit processing pipeline.

### shellcheck:SC2310:rank_7:SR 3.3

- Source rule: `SC2310` — This function is invoked in an 'if' condition so set -e will be disabled. Invoke separately if failures should cause the script to exit.
- Rank: `7`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.700393`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Indirect`

**Security objective:** Security functionality verification

**Justification:** Ensuring scripts do not fail silently is a general software quality practice that supports the reliability of security functions, but it is not a direct verification of security functionality.

**Caveat:** None

### shellcheck:SC2311:rank_4:SR 7.1

- Source rule: `SC2311` — Bash implicitly disabled set -e for this function invocation because it's inside a command substitution. Add set -e; before it or enable inherit_errexit.
- Rank: `4`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `0.937703`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** System robustness and reliability

**Justification:** While the rule improves script reliability, it is a general software quality issue. It is only tangentially related to DoS protection if the script in question is a critical component whose failure could lead to a system-wide DoS or inability to enter a degraded mode.

**Caveat:** The relationship is highly contextual and depends on whether the script is part of the control system's critical path.

### shellcheck:SC2311:rank_7:SR 3.6

- Source rule: `SC2311` — Bash implicitly disabled set -e for this function invocation because it's inside a command substitution. Add set -e; before it or enable inherit_errexit.
- Rank: `7`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `0.861114`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `functional`
- Directness: `indirect`

**Security objective:** Deterministic output

**Justification:** The rule ensures that a script fails predictably when an error occurs, which aligns with the concept of deterministic behavior, though it is not specifically about control system outputs.

**Caveat:** The scope of the rule is general scripting, not industrial control system output states.

### shellcheck:SC2311:rank_8:SR 3.7

- Source rule: `SC2311` — Bash implicitly disabled set -e for this function invocation because it's inside a command substitution. Add set -e; before it or enable inherit_errexit.
- Rank: `8`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.84363`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `functional`
- Directness: `direct`

**Security objective:** Error handling

**Justification:** The rule directly addresses the failure to handle error conditions in a script, ensuring that errors are not ignored, which is a fundamental aspect of robust error handling.

**Caveat:** The rule focuses on script execution logic rather than the security-sensitive disclosure of error messages.

### shellcheck:SC2312:rank_1:SR 3.2 RE 1

- Source rule: `SC2312` — Consider invoking this command separately to avoid masking its return value (or use '|| true' to ignore).
- Rank: `1`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Malicious code protection

**Justification:** While the rule improves script robustness by preventing execution of commands in incorrect contexts (e.g., wrong directory), it is a general software quality issue rather than a specific malicious code protection mechanism.

**Caveat:** The rule prevents accidental execution of commands in wrong paths, which could be exploited, but it is not a dedicated malicious code protection mechanism.

### shellcheck:SC2312:rank_2:SR 3.6

- Source rule: `SC2312` — Consider invoking this command separately to avoid masking its return value (or use '|| true' to ignore).
- Rank: `2`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `0.976941`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Deterministic output

**Justification:** The rule ensures that scripts fail predictably when a dependency fails, which aligns with the goal of deterministic behavior. However, it is a general programming practice rather than a control system output state management mechanism.

**Caveat:** The scope of the rule is general shell scripting, not control system output states.

### shellcheck:SC2312:rank_3:SR 3.7

- Source rule: `SC2312` — Consider invoking this command separately to avoid masking its return value (or use '|| true' to ignore).
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.90287`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `moderate`

**Security objective:** Error handling

**Justification:** The rule directly addresses the failure to handle error conditions in shell scripts, ensuring that errors are propagated and handled rather than ignored, which is a fundamental aspect of robust error handling.

**Caveat:** The rule is specific to shell scripting and does not cover all aspects of IACS error handling.

### shellcheck:SC2312:rank_10:SR 3.2

- Source rule: `SC2312` — Consider invoking this command separately to avoid masking its return value (or use '|| true' to ignore).
- Rank: `10`
- IEC target: `SR 3.2` — Malicious code protection
- Relative score: `0.692712`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling to prevent unintended system state changes

**Justification:** The rule prevents command masking, which could lead to unintended execution of commands (e.g., cd /etc) if a previous command fails. While this is a general software robustness issue, it indirectly supports malicious code protection by preventing the system from entering an insecure state that could be exploited.

**Caveat:** This is a general programming best practice rather than a specific malicious code protection mechanism.

### shellcheck:SC2313:rank_2:SR 3.5

- Source rule: `SC2313` — Quote array indices to avoid them expanding as globs.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.953716`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `direct`
- Directness: `medium`

**Security objective:** Input validation and sanitization

**Justification:** The rule addresses shell globbing vulnerabilities where unquoted input is interpreted as a pattern. This is a form of input validation/sanitization, ensuring that data is treated as data rather than being interpreted as a command or path pattern.

**Caveat:** The rule is specific to shell syntax, whereas SR 3.5 is a broader requirement for industrial control inputs.

### shellcheck:SC2313:rank_8:SR 3.7

- Source rule: `SC2313` — Quote array indices to avoid them expanding as globs.
- Rank: `8`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.809735`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and predictable system behavior

**Justification:** While the rule is primarily about syntax, failing to quote variables can lead to unexpected runtime behavior or logic errors that might be interpreted as an error condition. However, it does not directly address the security-sensitive error handling requirements of SR 3.7.

**Caveat:** The relationship is very weak and likely coincidental.

### shellcheck:SC2314:rank_1:SR 5.2 RE 3

- Source rule: `SC2314` — In bats, ! does not cause a test failure.
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and fail-safe behavior

**Justification:** While the rule ensures test failures are correctly identified (which is good practice for software quality), it is a development-time testing issue rather than a runtime 'fail close' mechanism for boundary protection.

**Caveat:** The rule improves test reliability, which indirectly supports the development of robust systems, but it does not implement the specific 'fail close' requirement defined in SR 5.2.

### shellcheck:SC2314:rank_2:SR 3.7

- Source rule: `SC2314` — In bats, ! does not cause a test failure.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.983566`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling

**Justification:** The rule ensures that errors in test scripts are correctly caught. This aligns with the general principle of identifying and handling error conditions, though it is specific to the testing environment rather than the production control system.

**Caveat:** The rule applies to test code (Bats), not the production control system logic.

### shellcheck:SC2315:rank_1:SR 5.2 RE 3

- Source rule: `SC2315` — In bats, ! does not cause a test failure. Fold the ! into the conditional!
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and fail-safe behavior

**Justification:** Similar to SC2314, this rule improves the reliability of test suites. It does not directly implement the 'fail close' requirement for boundary protection mechanisms in a production environment.

**Caveat:** The rule applies to test code (Bats), not the production control system logic.

### shellcheck:SC2315:rank_2:SR 3.7

- Source rule: `SC2315` — In bats, ! does not cause a test failure. Fold the ! into the conditional!
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.984458`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Error Handling Logic`
- Directness: `Indirect`

**Security objective:** Ensure reliable error detection and system state reporting

**Justification:** The rule addresses a specific technical flaw in Bats testing where negated commands fail to trigger error exits. While this improves the reliability of test suites (which is a form of error handling), it is a development-time testing issue rather than a runtime control system error handling mechanism as described in SR 3.7.

**Caveat:** The relationship is limited to the general concept of 'error handling' but differs in scope (testing vs. operational control system behavior).

### shellcheck:SC2317:rank_1:SR 1.11

- Source rule: `SC2317` — Command appears to be unreachable. Check usage (or ignore if invoked indirectly).
- Rank: `1`
- IEC target: `SR 1.11` — Unsuccessful login attempts
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Code quality and logic flow

**Justification:** While unreachable code can indicate logic errors, it is not directly related to the enforcement of login attempt limits or account lockout mechanisms.

**Caveat:** Unreachable code might hide security-critical logic, but the rule itself is a general code quality check.

### shellcheck:SC2317:rank_3:SR 3.7

- Source rule: `SC2317` — Command appears to be unreachable. Check usage (or ignore if invoked indirectly).
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.908165`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling and code quality

**Justification:** Unreachable code can be a symptom of poor error handling, but the rule does not specifically address the security-sensitive aspects of error reporting required by SR 3.7.

**Caveat:** None

### shellcheck:SC2319:rank_1:SR 5.2 RE 3

- Source rule: `SC2319` — This $? refers to a condition, not a command. Assign to a variable to avoid it being overwritten.
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and state management

**Justification:** While the rule is about shell scripting logic, the requirement for 'fail close' mechanisms relies on the system correctly identifying and acting upon operational failures. Incorrectly handling exit codes could lead to a failure to trigger a 'fail close' state.

**Caveat:** The rule is a general coding best practice and not specifically designed for security-critical fail-close logic.

### shellcheck:SC2319:rank_2:SR 3.7

- Source rule: `SC2319` — This $? refers to a condition, not a command. Assign to a variable to avoid it being overwritten.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.868128`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `moderate`

**Security objective:** Reliable error handling

**Justification:** The rule ensures that error codes are correctly captured and preserved. This is essential for the control system to accurately identify error conditions and perform remediation, which is the core of SR 3.7.

**Caveat:** The rule is generic to shell scripts and not specific to IACS error handling.

### shellcheck:SC2319:rank_3:SR 3.6

- Source rule: `SC2319` — This $? refers to a condition, not a command. Assign to a variable to avoid it being overwritten.
- Rank: `3`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `0.823734`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Deterministic behavior

**Justification:** Correctly handling exit codes is a prerequisite for deterministic behavior, but the rule itself is a low-level syntax/logic check rather than a mechanism for setting outputs to a predetermined state.

**Caveat:** The relationship is too distant to be considered a direct implementation of the requirement.

### shellcheck:SC2320:rank_1:SR 3.6

- Source rule: `SC2320` — This $? refers to echo/printf, not a previous command. Assign to variable to avoid it being overwritten.
- Rank: `1`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Deterministic behavior and error handling

**Justification:** While the rule is a coding best practice, ensuring that error codes are correctly captured and handled is a prerequisite for robust error handling and deterministic behavior in control systems.

**Caveat:** The rule is a general programming bug fix, not a specific security control for deterministic output.

### shellcheck:SC2320:rank_3:SR 3.7

- Source rule: `SC2320` — This $? refers to echo/printf, not a previous command. Assign to variable to avoid it being overwritten.
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.865638`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supporting`
- Directness: `moderate`

**Security objective:** Robust error handling

**Justification:** Correctly capturing and checking exit codes is fundamental to implementing effective error handling and remediation, which is the core requirement of SR 3.7.

**Caveat:** This is a low-level implementation detail supporting a high-level requirement.

### shellcheck:SC2320:rank_4:SR 2.10

- Source rule: `SC2320` — This $? refers to echo/printf, not a previous command. Assign to variable to avoid it being overwritten.
- Rank: `4`
- IEC target: `SR 2.10` — Response to audit processing failures
- Relative score: `0.82707`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Reliable audit processing

**Justification:** If audit processing scripts fail to correctly capture exit codes, they may fail to detect or respond to audit processing failures. However, the rule is too generic to be considered a direct control for SR 2.10.

**Caveat:** The relationship is purely incidental to the implementation of audit scripts.

### shellcheck:SC2324:rank_3:SR 3.5

- Source rule: `SC2324` — var+=1 will append, not increment. Use (( var += 1 )), declare -i var, or quote number to silence.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.9814`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and data integrity

**Justification:** The rule prevents logic errors caused by unexpected data types (string vs integer). While not a direct security validation of external input, ensuring variables are treated as intended prevents malformed data processing, which aligns with the broader goal of input validation.

**Caveat:** This is a general programming correctness rule rather than a dedicated security input validation mechanism.

### shellcheck:SC2329:rank_2:SR 7.7

- Source rule: `SC2329` — This function is never invoked. Check usage (or ignored if invoked indirectly).
- Rank: `2`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.826638`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Least functionality

**Justification:** Removing unused functions is a form of reducing the attack surface and adhering to the principle of least functionality, though the rule is primarily a code quality check for dead code.

**Caveat:** The rule is a static analysis check for dead code, not a deliberate security policy to disable unnecessary services.

### shellcheck:SC2329:rank_4:SR 3.3

- Source rule: `SC2329` — This function is never invoked. Check usage (or ignored if invoked indirectly).
- Rank: `4`
- IEC target: `SR 3.3` — Security functionality verification
- Relative score: `0.744115`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Security functionality verification

**Justification:** While cleaning up unused code is good practice, it does not directly support the verification of security functions or the reporting of anomalies as required by SR 3.3.

**Caveat:** The relationship is very weak; dead code removal is a maintenance task, not a security verification task.

### shellcheck:SC2331:rank_1:SR 3.7

- Source rule: `SC2331` — For file existence, prefer standard -e over legacy -a.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Robust error handling and predictable behavior

**Justification:** The rule prevents ambiguous conditional logic that could lead to incorrect script execution. While not a direct security control, avoiding ambiguous logic is a best practice for robust error handling.

**Caveat:** The relationship is weak as the rule is primarily about portability and avoiding shell-specific bugs rather than security-critical error handling.

### shellcheck:SC2331:rank_2:SR 3.5

- Source rule: `SC2331` — For file existence, prefer standard -e over legacy -a.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.999368`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and predictable execution

**Justification:** The rule ensures that file existence checks behave as expected. Insecure or ambiguous file checks can lead to logic errors that might be exploited, though this is a stretch for this specific rule.

**Caveat:** The rule is more about language correctness than security-focused input validation.

### shellcheck:SC2332:rank_1:SR 5.2 RE 3

- Source rule: `SC2332` — [ ! -o opt ] is always true because -o becomes logical OR. Use [[ ]] or ! [ -o opt ].
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Logic correctness in boundary protection

**Justification:** The rule fixes a logic error where a condition is always true. If this condition were part of a security boundary check, the failure to correctly evaluate the condition could lead to a bypass of security controls, though the rule itself is generic.

**Caveat:** The rule is a general coding best practice; its application to 'fail close' is highly contextual.

### shellcheck:SC2332:rank_2:SR 3.5

- Source rule: `SC2332` — [ ! -o opt ] is always true because -o becomes logical OR. Use [[ ]] or ! [ -o opt ].
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.851756`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and logic integrity

**Justification:** The rule prevents logic errors in conditional statements. If these statements validate inputs, the fix ensures the validation logic actually executes as intended rather than defaulting to a 'true' state.

**Caveat:** The rule is not specifically about input validation, but about shell syntax correctness.

### shellcheck:SC2332:rank_4:SR 3.7

- Source rule: `SC2332` — [ ! -o opt ] is always true because -o becomes logical OR. Use [[ ]] or ! [ -o opt ].
- Rank: `4`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.69128`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Error handling and logic reliability

**Justification:** The rule ensures that conditional logic behaves as expected. If used in error handling routines, it prevents the logic from failing to evaluate correctly, which is a prerequisite for effective error handling.

**Caveat:** The rule is a general syntax fix, not a specific error handling security control.

### shellcheck:SC2333:rank_1:SR 3.5

- Source rule: `SC2333` — You probably wanted || here, otherwise it's always false.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Logic correctness in input handling

**Justification:** The rule identifies a logic error in a conditional check. While this specific instance is a general programming error, logic errors in input validation routines can lead to security vulnerabilities where inputs are incorrectly processed or bypassed. It is tangentially related to ensuring input validation logic functions as intended.

**Caveat:** The rule is a general-purpose code quality check, not a security-specific input validation mechanism.

### shellcheck:SC2334:rank_1:SR 3.5

- Source rule: `SC2334` — You probably wanted || here, otherwise it's always false.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and logic correctness

**Justification:** While the rule is a general logic fix, it is being applied to validate return codes (inputs to the logic flow). This relates tangentially to ensuring the control system processes inputs correctly, though it is not a security-specific validation.

**Caveat:** The rule is a general programming best practice rather than a security-specific input validation mechanism.

### shellcheck:SC2334:rank_3:SR 7.1

- Source rule: `SC2334` — You probably wanted || here, otherwise it's always false.
- Rank: `3`
- IEC target: `SR 7.1` — Denial of service protection
- Relative score: `0.806913`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Logic correctness for error handling

**Justification:** The rule identifies a logic error in error handling code. While this specific instance relates to process termination codes, it is only tangentially related to the broader requirement of maintaining system operation during a DoS event.

**Caveat:** The rule is a general coding best practice and not specifically designed for DoS mitigation.

### shellcheck:SC2334:rank_5:SR 3.6

- Source rule: `SC2334` — You probably wanted || here, otherwise it's always false.
- Rank: `5`
- IEC target: `SR 3.6` — Deterministic output
- Relative score: `0.78893`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Deterministic system behavior

**Justification:** The rule ensures that logic branches execute as intended. If the logic branch is responsible for setting a system to a 'predetermined state' during a failure, this rule helps ensure that logic is actually reachable.

**Caveat:** The rule is generic and not specific to the security-critical state transitions required by SR 3.6.

### shellcheck:SC3001:rank_1:SR 1.2

- Source rule: `SC3001` — In POSIX sh, process substitution is undefined.
- Rank: `1`
- IEC target: `SR 1.2` — Software process and device identification and authentication
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Software portability and reliability

**Justification:** While the rule ensures script portability, it does not directly relate to the identification and authentication of software processes. It is only tangentially related to ensuring that the environment behaves as expected, which is a prerequisite for reliable authentication.

**Caveat:** The rule is primarily about POSIX compatibility, not security.

### shellcheck:SC3003:rank_1:SR 3.5

- Source rule: `SC3003` — In POSIX sh, $'..' is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and interpreter safety

**Justification:** While the rule is primarily about POSIX compatibility, using non-standard shell features can lead to unexpected behavior in scripts that process inputs. The rationale for SR 3.5 mentions preventing content from being unintentionally interpreted as commands, which is tangentially related to shell script robustness.

**Caveat:** The rule is primarily a compatibility check, not a security-focused input validation check.

### shellcheck:SC3004:rank_1:SR 3.5

- Source rule: `SC3004` — In POSIX sh, $".." is undefined
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Input validation and secure coding

**Justification:** While the rule is primarily about portability, the use of non-standard syntax or improper handling of localized strings can lead to unexpected behavior or injection vulnerabilities if not handled correctly.

**Caveat:** The rule is primarily a portability check, not a security-focused input validation check.

### shellcheck:SC3004:rank_3:SR 3.7

- Source rule: `SC3004` — In POSIX sh, $".." is undefined
- Rank: `3`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.957954`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Error handling and secure coding

**Justification:** The rule relates to how strings are processed; improper handling of localized strings or undefined syntax can lead to runtime errors that might be exploited or reveal system information.

**Caveat:** The rule is primarily a portability check, not an error handling security check.

### shellcheck:SC3006:rank_2:SR 3.5

- Source rule: `SC3006` — In POSIX sh, standalone ((..)) is undefined.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.901244`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** While the rule is primarily about POSIX compliance, the use of non-standard shell syntax can lead to unexpected behavior in scripts that process inputs. SR 3.5 requires validation of inputs to prevent exploitation, and using standard, well-defined syntax is a best practice for robust input handling.

**Caveat:** The rule is a portability check, not a security-focused input validation check.

### shellcheck:SC3009:rank_2:SR 3.5

- Source rule: `SC3009` — In POSIX sh, brace expansion is undefined.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.833296`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule addresses shell portability and syntax ambiguity. While SR 3.5 requires input validation to prevent exploitation, this rule is primarily about code portability rather than security-critical input sanitization.

**Caveat:** The rule is a best practice for portability, not a direct security control for input validation.

### shellcheck:SC3010:rank_2:SR 3.7

- Source rule: `SC3010` — In POSIX sh, [[ ]] is undefined.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.901563`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Error handling

**Justification:** The rule identifies undefined behavior in shell scripts. If such undefined behavior leads to runtime errors, it could theoretically impact error handling, but the rule itself is about syntax, not security-sensitive error reporting.

**Caveat:** The relationship is purely incidental to potential runtime errors.

### shellcheck:SC3012:rank_1:SR 3.5

- Source rule: `SC3012` — In POSIX sh, lexicographical \< is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell portability, using non-standard operators can lead to unexpected behavior in scripts that process inputs, which is tangentially related to input validation.

**Caveat:** The rule is a coding standard for portability, not a security-focused input validation check.

### shellcheck:SC3014:rank_3:SR 3.5

- Source rule: `SC3014` — In POSIX sh, == in place of = is undefined.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.929145`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell portability, using non-standard syntax can lead to unexpected behavior in different environments, which is tangentially related to input processing, but it is not a security-focused input validation rule.

**Caveat:** The rule is a compatibility check, not a security validation check.

### shellcheck:SC3015:rank_1:SR 3.5

- Source rule: `SC3015` — In POSIX sh, =~ regex matching is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is primarily about shell portability, the use of regex matching is a common mechanism for input validation. Ensuring the correct implementation of regex (or alternatives) is relevant to the robustness of input validation logic.

**Caveat:** The rule is a portability warning, not a security-focused input validation check.

### shellcheck:SC3015:rank_2:SR 3.2 RE 1

- Source rule: `SC3015` — In POSIX sh, =~ regex matching is undefined.
- Rank: `2`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.925038`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Malicious code protection

**Justification:** Regex matching is often used in security filters to detect malicious patterns. If the regex implementation is undefined or fails due to portability issues, the security filter might fail to execute correctly, potentially bypassing malicious code protection.

**Caveat:** The rule is a portability warning, not a direct security mechanism for malicious code detection.

### shellcheck:SC3016:rank_5:SR 3.7

- Source rule: `SC3016` — In POSIX sh, unary -v (in place of [ -n "${var+x}" ]) is undefined.
- Rank: `5`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.831393`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Software Robustness`
- Directness: `Indirect`

**Security objective:** Error handling and system stability

**Justification:** The rule ensures shell script portability, which prevents undefined behavior. While not directly related to security-sensitive error handling, avoiding undefined behavior contributes to overall system reliability and predictable error states.

**Caveat:** The rule is primarily about portability, not security-critical error handling.

### shellcheck:SC3023:rank_6:SR 3.5

- Source rule: `SC3023` — In POSIX sh, FDs outside 0-9 are undefined.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.775208`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and robust system operation

**Justification:** While SC3023 is primarily a portability issue, using undefined shell syntax can lead to unpredictable script behavior. SR 3.5 requires validating inputs to prevent unintended interpretation. There is a very weak, indirect link if the shell script is considered an 'input' to the system, but the rule is not a security control.

**Caveat:** The rule is a portability warning, not a security validation rule.

### shellcheck:SC3025:rank_1:SR 7.1 RE 1

- Source rule: `SC3025` — In POSIX sh, /dev/{tcp,udp} is undefined.
- Rank: `1`
- IEC target: `SR 7.1 RE 1` — Manage communication loads
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Communication management

**Justification:** The rule forces the use of explicit tools (like nc) instead of shell-specific pseudo-devices. While this improves code clarity, it does not inherently manage communication loads or mitigate DoS events.

**Caveat:** The rule is about syntax portability, not traffic shaping or load management.

### shellcheck:SC3025:rank_4:SR 7.7

- Source rule: `SC3025` — In POSIX sh, /dev/{tcp,udp} is undefined.
- Rank: `4`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.839224`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Least functionality

**Justification:** By forcing the use of explicit tools, it might indirectly encourage developers to be more aware of the network services they are invoking, but the rule itself is purely about shell portability.

**Caveat:** The rule does not restrict functionality; it only changes the syntax used to invoke it.

### shellcheck:SC3026:rank_1:SR 3.5

- Source rule: `SC3026` — In POSIX sh, ^ in place of ! in glob bracket expressions is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `Input Validation`
- Directness: `Direct`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule enforces the use of standard, well-defined syntax for pattern matching. Using undefined or non-standard syntax can lead to unexpected behavior or bypasses in input processing, which directly relates to the requirement for validating the syntax of inputs.

**Caveat:** The rule is primarily about POSIX compliance, but in a security context, ensuring predictable behavior of pattern matching is a form of input validation.

### shellcheck:SC3026:rank_4:SR 3.2 RE 1

- Source rule: `SC3026` — In POSIX sh, ^ in place of ! in glob bracket expressions is undefined.
- Rank: `4`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.793599`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Input Validation`
- Directness: `Indirect`

**Security objective:** Malicious code protection

**Justification:** While ensuring correct syntax is a general security best practice, this rule is specifically about shell portability rather than malicious code protection mechanisms at entry/exit points.

**Caveat:** The relationship is weak and likely coincidental based on the broad nature of input validation.

### shellcheck:SC3028:rank_1:SR 3.8 RE 3

- Source rule: `SC3028` — In POSIX sh, VARIABLE is undefined.
- Rank: `1`
- IEC target: `SR 3.8 RE 3` — Randomness of session IDs
- Relative score: `1.0`
- Gemini verdict: **YES**
- Confidence: `5/5`
- Relation type: `Direct Support`
- Directness: `Direct`

**Security objective:** Ensure secure and unpredictable generation of session identifiers.

**Justification:** The rule explicitly suggests using a robust method for generating random values (via awk/rand) when the shell's native random variable is unavailable, which directly aligns with the requirement to use accepted sources of randomness for session IDs.

**Caveat:** The rule is primarily about shell portability, but the suggested fix provides the necessary mechanism for randomness.

### shellcheck:SC3029:rank_1:SR 3.5

- Source rule: `SC3029` — In POSIX sh, |& in place of 2>&1 | is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Indirect Support`
- Directness: `Indirect`

**Security objective:** Input validation and command injection prevention.

**Justification:** While the rule is about shell syntax portability, ensuring that scripts are interpreted by the correct shell (as the rule enforces) can prevent unintended command execution or misinterpretation of inputs, which is tangentially related to input validation.

**Caveat:** The rule is primarily a portability check, not a security-focused input validation check.

### shellcheck:SC3030:rank_1:SR 3.5

- Source rule: `SC3030` — In POSIX sh, arrays are undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and robust coding

**Justification:** While the rule is about language syntax (arrays in POSIX sh), the rationale for SR 3.5 mentions that inputs passed to interpreters should be pre-screened. Using non-portable features can lead to unexpected behavior, but this is a stretch for 'input validation' in the security sense.

**Caveat:** The rule is a static analysis check for language compliance, not a security-focused input validation check.

### shellcheck:SC3034:rank_1:SR 3.5

- Source rule: `SC3034` — In POSIX sh, $(<file) is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation and predictable behavior

**Justification:** The rule addresses undefined behavior in shell scripts which can lead to unexpected results. While not direct input validation, ensuring predictable script execution is a prerequisite for robust input handling.

**Caveat:** The rule is primarily about POSIX compliance rather than security-focused input validation.

### shellcheck:SC3035:rank_7:SR 3.5

- Source rule: `SC3035` — In POSIX sh,  <file  is undefined.
- Rank: `7`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.730606`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule identifies undefined shell syntax. While syntax errors can lead to unexpected behavior, this is primarily a portability issue rather than a security-focused input validation mechanism as defined in SR 3.5.

**Caveat:** The rule is a static syntax check, not a runtime input validation mechanism.

### shellcheck:SC3039:rank_1:SR 3.5

- Source rule: `SC3039` — In POSIX sh, let is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule encourages using standard POSIX arithmetic expansion instead of non-standard 'let'. While this improves code portability and robustness, it is not a direct security control for input validation as defined in SR 3.5, which focuses on preventing injection or malformed data processing.

**Caveat:** The rule is primarily a compatibility/best-practice check rather than a security-focused input validation check.

### shellcheck:SC3040:rank_1:SR 5.2 RE 3

- Source rule: `SC3040` — In POSIX sh, set option [name] is undefined.
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Fail close

**Justification:** The rule discusses implementing pipefail logic to handle command failures in scripts. While this relates to error handling, it is a stretch to equate shell script error handling with the high-level requirement of boundary protection mechanisms failing closed.

**Caveat:** The rule is about script robustness, not boundary protection.

### shellcheck:SC3041:rank_8:SR 7.7

- Source rule: `SC3041` — In POSIX sh, set flag -E is undefined
- Rank: `8`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.74017`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Shell portability and configuration

**Justification:** While the rule is primarily about portability, ensuring that scripts only use the features they are intended to use (and not relying on undefined behavior) aligns loosely with the principle of least functionality by avoiding unnecessary or unintended shell features.

**Caveat:** The relationship is very weak as the rule is a syntax/portability check, not a security-focused restriction of system services.

### shellcheck:SC3042:rank_4:SR 7.6

- Source rule: `SC3042` — In POSIX sh, set flag --default is undefined
- Rank: `4`
- IEC target: `SR 7.6` — Network and security configuration settings
- Relative score: `0.933006`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Configuration Management`
- Directness: `Indirect`

**Security objective:** Ensure system configuration consistency and portability

**Justification:** The rule enforces correct shell configuration to match the interpreter, which relates to ensuring the system operates within its intended configuration parameters as required by SR 7.6.

**Caveat:** The rule is primarily about script portability rather than security configuration management, though consistent configuration is a prerequisite for security.

### shellcheck:SC3042:rank_6:SR 7.7

- Source rule: `SC3042` — In POSIX sh, set flag --default is undefined
- Rank: `6`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `0.898543`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `Least Functionality`
- Directness: `Indirect`

**Security objective:** Restrict unnecessary functions

**Justification:** By ensuring scripts use the correct shell and features, one could argue it prevents the accidental invocation of non-standard or unnecessary shell features, aligning loosely with least functionality.

**Caveat:** The rule is about syntax compatibility, not the restriction of system-level functions or services.

### shellcheck:SC3043:rank_2:SR 3.5

- Source rule: `SC3043` — In POSIX sh, local is undefined.
- Rank: `2`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.963885`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Variable scoping and shell portability

**Justification:** While the rule is about shell portability, the suggested fix (prefixing variables) is a coding convention that can help prevent variable collisions, which is a minor aspect of robust code, but it does not address input validation as defined in SR 3.5.

**Caveat:** The relationship is purely coincidental based on code quality practices.

### shellcheck:SC3043:rank_7:SR 4.2 RE 1

- Source rule: `SC3043` — In POSIX sh, local is undefined.
- Rank: `7`
- IEC target: `SR 4.2 RE 1` — Purging of shared memory resources
- Relative score: `0.80695`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Resource isolation and data leakage prevention

**Justification:** The rule encourages avoiding global variable pollution by using local variables. While this is a coding best practice, it is only tangentially related to preventing information transfer via shared memory resources (SR 4.2), as shell variables are not typically considered 'shared memory' in the context of system-level security.

**Caveat:** The relationship is very weak and likely a false positive based on lexical similarity.

### shellcheck:SC3045:rank_1:SR 7.7

- Source rule: `SC3045` — In POSIX sh, some-command-with-flag is undefined.
- Rank: `1`
- IEC target: `SR 7.7` — Least functionality
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Least functionality

**Justification:** The rule warns about using non-portable shell features. While not directly about disabling services, using non-standard or unintended shell features can lead to unexpected behavior or the execution of code in environments where it was not intended, which touches upon the principle of least functionality.

**Caveat:** The relationship is weak; the rule is primarily about portability, not security-focused service restriction.

### shellcheck:SC3047:rank_1:SR 5.2 RE 3

- Source rule: `SC3047` — In POSIX sh, trapping ERR is undefined.
- Rank: `1`
- IEC target: `SR 5.2 RE 3` — Fail close
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and system stability

**Justification:** While the rule is about shell compatibility, using traps for error handling is a mechanism for system stability. However, it does not relate to the specific boundary protection failure requirements of SR 5.2.

**Caveat:** The relationship is purely coincidental based on the word 'trap' and 'error'.

### shellcheck:SC3047:rank_2:SR 3.7

- Source rule: `SC3047` — In POSIX sh, trapping ERR is undefined.
- Rank: `2`
- IEC target: `SR 3.7` — Error handling
- Relative score: `0.917266`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling

**Justification:** The rule concerns the implementation of error traps. SR 3.7 requires error handling that does not leak sensitive information. While the rule is about syntax, the underlying mechanism (traps) is a component of error handling.

**Caveat:** The rule is a syntax compatibility issue, not a security-focused error handling design.

### shellcheck:SC3049:rank_1:SR 3.7

- Source rule: `SC3049` — In POSIX sh, using lower/mixed case for signal names is undefined.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Low`

**Security objective:** Robust error handling and predictable system behavior

**Justification:** While the rule is primarily about POSIX syntax, using undefined or non-standard signal names can lead to unpredictable script behavior or failure to handle signals correctly. This could theoretically impact the reliability of error handling mechanisms, which is the focus of SR 3.7.

**Caveat:** The relationship is weak as the rule is a syntax check rather than a security-focused error handling requirement.

### shellcheck:SC3050:rank_4:SR 4.1 RE 1

- Source rule: `SC3050` — In POSIX sh, printf %q is undefined.
- Rank: `4`
- IEC target: `SR 4.1 RE 1` — Protection of confidentiality at rest or in transit via untrusted networks
- Relative score: `0.958627`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Secure remote access and data handling

**Justification:** The rule warns about using non-portable shell features for escaping strings in remote commands (ssh). While the rule is about portability, the problematic code pattern involves remote command execution, which is relevant to the security of remote access sessions.

**Caveat:** The rule is primarily about shell portability, not security, but the context of the problematic code (ssh) touches on remote access security.

### shellcheck:SC3050:rank_5:SR 3.2 RE 1

- Source rule: `SC3050` — In POSIX sh, printf %q is undefined.
- Rank: `5`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.940014`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input sanitization and command injection prevention

**Justification:** The rule addresses shell command injection risks by highlighting non-portable escaping. While not a direct 'malicious code protection' mechanism, proper input handling is a prerequisite for preventing command injection, which is a form of malicious code execution.

**Caveat:** The rule is primarily about POSIX portability, not security, though it touches on injection vulnerabilities.

### shellcheck:SC3052:rank_1:SR 3.7

- Source rule: `SC3052` — In POSIX sh, arithmetic base conversion is undefined
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Robust error handling and input processing

**Justification:** While the rule is about portability, using undefined shell features can lead to unexpected script behavior or errors. SR 3.7 requires handling errors without leaking exploitable information. The connection is weak as the rule is primarily about syntax compatibility.

**Caveat:** The rule is a static analysis check for portability, not a security-focused error handling mechanism.

### shellcheck:SC3052:rank_3:SR 3.5

- Source rule: `SC3052` — In POSIX sh, arithmetic base conversion is undefined
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.846466`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation and syntax correctness

**Justification:** The rule identifies non-portable syntax. SR 3.5 requires validating input syntax to prevent exploitation. While both involve syntax, the rule is about shell compatibility, not security-critical input validation.

**Caveat:** The rule does not address malicious input or security-critical data validation.

### shellcheck:SC3053:rank_1:SR 3.7

- Source rule: `SC3053` — In POSIX sh, indirect expansion is undefined.
- Rank: `1`
- IEC target: `SR 3.7` — Error handling
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Secure coding practices and error prevention

**Justification:** The rule warns about indirect expansion and suggests using 'eval', which can introduce code injection vulnerabilities if not handled correctly. This relates to the broader goal of secure error handling and avoiding exploitable code patterns, though the rule itself is primarily about shell compatibility.

**Caveat:** The rule is primarily a compatibility warning; the security implication is secondary and depends on the developer's implementation of the suggested 'eval' workaround.

### shellcheck:SC3053:rank_3:SR 3.5

- Source rule: `SC3053` — In POSIX sh, indirect expansion is undefined.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.918784`
- Gemini verdict: **YES**
- Confidence: `4/5`
- Relation type: `supportive`
- Directness: `medium`

**Security objective:** Input validation and secure command execution

**Justification:** The rule's rationale explicitly warns that using 'eval' (a common workaround for the rule) requires validating variable names to avoid code injection. This directly aligns with the requirement to validate input to prevent malicious command interpretation.

**Caveat:** The rule is a compatibility warning, but the provided rationale explicitly addresses the security concern of command injection, which is central to SR 3.5.

### shellcheck:SC3053:rank_8:SR 3.2 RE 1

- Source rule: `SC3053` — In POSIX sh, indirect expansion is undefined.
- Rank: `8`
- IEC target: `SR 3.2 RE 1` — Malicious code protection on entry and exit points
- Relative score: `0.764871`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `Indirect`
- Directness: `Weak`

**Security objective:** Code injection prevention

**Justification:** The rule mentions that improper use of 'eval' can lead to code injection. While this is a security concern, it is a general software development practice rather than a specific mechanism for malicious code protection at network entry/exit points.

**Caveat:** The relationship is only relevant if the shell script is acting as an entry/exit point for the control system.

### shellcheck:SC3057:rank_3:SR 3.5

- Source rule: `SC3057` — In POSIX sh, string indexing is undefined.
- Rank: `3`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.852237`
- Gemini verdict: **MAYBE**
- Confidence: `2/5`
- Relation type: `indirect`
- Directness: `low`

**Security objective:** Input validation

**Justification:** The rule addresses shell compatibility issues with string indexing. While the rule itself is about portability, the rationale mentions that inputs passed to interpreters should be pre-screened. Using non-standard syntax can lead to unexpected behavior, which is a form of input handling concern, though not directly related to the security-focused input validation described in SR 3.5.

**Caveat:** The rule is primarily a portability/compatibility warning, not a security-specific input validation check.

### shellcheck:SC3060:rank_1:SR 3.5

- Source rule: `SC3060` — In POSIX sh, string replacement is undefined.
- Rank: `1`
- IEC target: `SR 3.5` — Input validation
- Relative score: `1.0`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Input validation

**Justification:** While the rule is about shell syntax compatibility, the suggested fix (using sed) involves string manipulation. The requirement mentions that inputs passed to interpreters should be pre-screened to prevent unintended interpretation, which is tangentially related to how strings are processed.

**Caveat:** The rule is primarily about portability, not security-focused input validation.

### shellcheck:SC3061:rank_6:SR 3.5

- Source rule: `SC3061` — In POSIX sh, read without a variable is undefined.
- Rank: `6`
- IEC target: `SR 3.5` — Input validation
- Relative score: `0.681892`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** Code robustness and input handling

**Justification:** While the rule is about POSIX compliance, using undefined shell behavior can lead to unpredictable script execution, which is tangentially related to the robustness of input processing, though it does not directly address the security validation of industrial process inputs.

**Caveat:** The rule is primarily about portability, not security-critical input validation.

### shellcheck:SC3065:rank_2:SR 4.2 RE 1

- Source rule: `SC3065` — In POSIX sh, test -k is undefined.
- Rank: `2`
- IEC target: `SR 4.2 RE 1` — Purging of shared memory resources
- Relative score: `0.800714`
- Gemini verdict: **MAYBE**
- Confidence: `3/5`
- Relation type: `indirect`
- Directness: `weak`

**Security objective:** File system permissions and resource integrity

**Justification:** The rule checks for the sticky bit, which is a file system permission mechanism. While the rule is about portability, the sticky bit itself is a security feature related to preventing unauthorized file deletion/modification, which is tangentially related to resource protection, though not specifically shared memory.

**Caveat:** The rule is purely about shell portability, not the security configuration of the sticky bit itself.

## Human / Gemini Disagreements

No human/Gemini disagreements recorded.
