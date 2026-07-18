# Job Application Assistant for Pedro Serio

<!-- SETUP: This file is populated by running /setup -->
<!-- After running /setup, all [PLACEHOLDER] tokens will be replaced with your actual information -->

## Role
This repo is a job application workspace. The AI assistant acts as a career advisor and application assistant for Pedro Serio, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** Pedro Serio
- **Location:** São Paulo, Brazil
- **Languages:** Portuguese (native), English (fluent), Spanish (basic)
- **Status:** Employed (Bioinformatics Analyst at Genesis Genomics)
- **LinkedIn:** www.linkedin.com/in/pedro-serio-708a4a140
- **Github:** https://github.com/Karksus
- **Email:** pedroaserio@gmail.com

### Education
- **MBA in Data Science and Analytics** (2023–2025) - ESALQ/USP
- **PhD in Genomics and Transcriptomics in Oncology** (2018–2023) - FMUSP/ICESP
  - Thesis: "Mutational Profile of Young Adult Triple-Negative Breast Cancer Patients"
  - Topics: Oncogenomics, NGS, bioinformatics, translational research
- **Specialization in Cancer Molecular Biology** (2017–2018) - FMUSP/ICESP
- **Scientific Initiation in Cancer Molecular Biology** (2016) - UNIFESP
- **Bachelor's Degree in Biomedical Science (Molecular Biology)** (2012–2016) - UNIP

### Professional Experience
- **Cloud Infrastructure & Automation Engineer – R&D Team** (2025–Present) - **Genesis Genomics** (São Paulo, Brazil)
  - Architect, deploy, and validate highly scalable, cloud-native (AWS) and hybrid on-premises automation platforms, applying robust distributed computing patterns to handle multi-terabyte genomic datasets.
  - Engineer and maintain custom analytical microservices and Python-based internal toolkits, leveraging serverless cloud triggers (Lambda, SNS, SQS) to streamline background execution and data ingestion flows.
  - Implement and validate bioinformatics pipelines (Illumina DRAGEN) across cloud and on-premises infrastructure, reducing variant calling time from hours to minutes.
  - Apply Clean Code principles and defensive design patterns to complex production data pipelines, optimizing execution runtime, system maintainability, and pipeline reliability.

- **Cloud Systems & Operations Analyst – Operational Team** (2024–2025) - **Genesis Genomics** (São Paulo, Brazil)
  - Provided critical tier support, performance tuning, and incident troubleshooting for high-throughput data servers and infrastructure platforms under strict operational SLAs.
  - Managed daily AWS cloud environment operations (S3, IAM, DataSync, Lambda, CLI), ensuring stringent data security compliance, identity and access management, and optimized asset transfer workflows.
  - Led technical cross-functional initiatives to integrate internal laboratory information management systems (LIMS) with platform APIs, automating end-to-end service order data synchronization.
  - Administered variant analysis platforms (Emedgene, Franklin, Varstation) and operated Illumina sequencers (iSeq, NextSeq, NovaSeq 6000, NovaSeq X+) with 99.9% uptime.

- **Systems & Data Analyst** (2023–2024) - **Grupo Fleury – Genomics Center** (São Paulo, Brazil)

- **PhD Scientist & Data Developer** (2018–2023) - **Oncology Translational Research Center (CTO/ICESP)** (São Paulo, Brazil)

- **Laboratory Assistant** (2014–2016) - **Federal University of São Paulo (UNIFESP)** (São Paulo, Brazil)

### Technical Skills
- **Primary:** Bioinformatics, cloud computing (AWS), molecular biology, NGS, data science, data analytics
- **Programming:** Python, R, Bash
- **Workflow management:** Nextflow, WDL
- **Operating systems:** Linux, Windows, macOS
- **Software & platforms:** VS Code, Notepad++, Microsoft Office, REDCap, Tasy (Philips)
- **AWS services:** S3, Lambda, EC2, ECS, Batch, DynamoDB, SNS, SQS, IAM
- **Laboratory techniques:** NGS library preparation, DNA/RNA extraction, qPCR, Laser Capture Microdissection

### Certifications
- **AWS Certified Solutions Architect – Associate (SAA-C03)** - Amazon Web Services, 2025

### Publications
- Rodrigues LM et al. Prevalence of germline variants in Brazilian pancreatic carcinoma patients. Sci Rep (Nature), 2024.
- Serio PAMP et al. Somatic Mutational Profile of High-Grade Serous Ovarian Carcinoma and Triple-Negative Breast Carcinoma in Young and Elderly Patients. Cells, 2021.
- Katayama MLH et al. Stromal Cell Signature Associated with Response to Neoadjuvant Chemotherapy in Locally Advanced Breast Cancer. Cells, 2019.
- Encinas G et al. Somatic Mutations in Early-Onset Luminal Breast Cancer. Oncotarget, 2018.

### Book Chapter
- Invasion and Metastasis. In: Oncology: From the Molecule to the Clinic. 2022.

### Teaching Experience
- VI Course in Molecular Oncology – ICESP (2021): Organizing Committee member, Lecturer (Invasion and Metastasis in Cancer, Introduction to Genomics and Transcriptomics in Bioinformatics)

### Courses & Professional Training
- Architect in AWS – Fast Lane (2025)
- AWS Certified Solutions Architect Associate – SAA-C03 (2025)
- Bioinformatics for Biologists – Wellcome Connecting (2023)
- Data Science in Python – Michigan State University (2022)
- Bioinformatic Methods I – University of Toronto (2021)
- Introduction to Biostatistics – ICESP-FMUSP (2019)

### Behavioral Profile
- **Analytical thinker** - Strong background in research and data analysis
- **Cross-functional collaborator** - Experience working in multidisciplinary teams
- **Detail-oriented** - Essential for bioinformatics pipeline validation and quality control
- **Strengths:** Technical expertise in NGS and bioinformatics, AWS cloud computing, translational research
- **Growth areas:** Industry experience, software engineering best practices
- **Thrives in:** Research-oriented environments, data-driven decision-making, precision medicine

### What Excites You
- Translating complex biological data into actionable healthcare solutions
- Applying computational expertise to industry challenges in genomics and precision medicine
- Cloud-based solutions for bioinformatics at scale

### Target Sectors
- Genomics and precision medicine: Genesis Genomics, Illumina, Foundation Medicine
- Biotech/pharma: Roche, Novartis, AstraZeneca
- Healthtech: Philips, Tempus, Guardant Health
- Cloud/AWS in life sciences: AWS Health, Google Cloud Life Sciences

### Deal-breakers
- Roles requiring on-site work without relocation support in a city far from São Paulo
- Positions without focus on data analysis, bioinformatics, or cloud infrastructure
- Purely managerial roles with no technical depth

## Repo Structure
- `cv/` - LaTeX CV variants (moderncv template, banking style)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.claude/skills/` - AI skill definitions for the application workflow
- `.agents/skills/` - Job search CLI tools

## Workflow for New Job Applications
1. User provides a job posting (URL or text)
2. **Always evaluate fit first**: skills match, experience match, behavioral/culture match. Present this assessment to the user before proceeding.
3. If good fit: create targeted CV (`cv/main_<company>.tex`) and cover letter (`cover_letters/cover_<company>_<role>.tex`)
4. **Verify both documents** (see Verification Checklist below)
5. Prepare interview talking points based on the role requirements and your strengths

## Verification Checklist
After creating or updating a CV or cover letter, re-read the generated file and verify **all** of the following before presenting to the user. Report the results as a pass/fail checklist.

### Factual accuracy
- [ ] All claims match actual profile (CLAUDE.md / candidate profile) - no fabricated skills, experience, or achievements
- [ ] Job titles, dates, company names, and locations are correct
- [ ] Contact details are correct
- [ ] All company-specific claims (partnerships, products, technology, expansions) have been independently verified via WebFetch/WebSearch - do not trust reviewer agent research without verification

### Targeting
- [ ] Profile statement / opening paragraph is tailored to the specific role (not generic)
- [ ] Skills and experience bullets are reframed to match the job requirements
- [ ] Key job requirements are addressed (with gaps acknowledged where relevant)
- [ ] Nice-to-have requirements are highlighted where there is a match

### Consistency
- [ ] CV follows the standard 2-page moderncv/banking format
- [ ] Cover letter uses cover.cls template and established structure
- [ ] Tone is consistent across CV and cover letter
- [ ] No contradictions between CV and cover letter content

### Quality
- [ ] No LaTeX syntax errors (balanced braces, correct commands)
- [ ] No spelling or grammar errors
- [ ] Cover letter is addressed to the correct person (or "Dear Hiring Manager" if unknown)
- [ ] Cover letter fits approximately one page

### Compiled PDF verification (MANDATORY - never skip)
Both documents MUST be compiled and visually inspected via the Read tool on the PDF output. "Looks fine in the .tex" is not acceptable - LaTeX page-break decisions are unpredictable. Iterate until these all pass:
- [ ] CV compiled with **lualatex** (pdflatex often fails on modern MiKTeX with fontawesome5 font-expansion errors). Cover letter compiled with **xelatex** (cover.cls requires fontspec).
- [ ] **CV is exactly 2 pages** - not 1, not 3
- [ ] **No orphaned `\cventry` titles** - a job/education title must never sit at the bottom of a page with its bullets spilling to the next page. Use `\needspace{5\baselineskip}` before each `\cventry` to prevent this, and `\enlargethispage{2-3\baselineskip}` to rescue a trailing section that just barely spills
- [ ] **Cover letter is exactly 1 page** - signature block must fit with the body, never overflow
- [ ] **Cover letter bullet font matches body font** - `\lettercontent{}` must not wrap `\begin{itemize}...\end{itemize}` (the command's trailing `\\` errors on `\end{itemize}`, and moving itemize outside loses the Raleway font). Standard pattern: close `\lettercontent{}`, then wrap the list in `{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont \begin{itemize}...\end{itemize}\par}`

### ATS & keyword verification (CV)
ATS parsers read the PDF's embedded text layer, not the rendered page. Extract it with `pdftotext -layout` and verify what a parser sees. `pdftotext` (poppler) is optional - if missing, skip the parseability items with a warning and check keyword coverage from the visual PDF read instead.
- [ ] CV text layer extracts cleanly - no `(cid:*)` markers, `�` replacement characters, or text visible in the PDF but absent from the extraction
- [ ] Email and phone appear as **literal text** in the extraction (icon-glyph noise like `MOBILE-ALT`/`Envelope` is harmless, but a contact detail carried only by an icon or hyperlink is invisible to ATS)
- [ ] Reading order of the extracted text matches the visual order (single-column stock template is safe; multi-column custom templates are where this breaks)
- [ ] Posting keywords covered or honestly absent - synonym-only matches tightened to the posting's exact term where truthfully applicable, keywords the profile genuinely supports added to experience bullets, genuine gaps left visible and **never stuffed**
