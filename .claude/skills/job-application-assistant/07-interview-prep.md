# Interview Preparation Guide

<!-- SETUP: STAR examples are personalized by running /setup based on your actual experience -->

## STAR Format

Structure answers as: **Situation** (context), **Task** (your responsibility), **Action** (what you did), **Result** (outcome).

Keep answers to 1-2 minutes. Be specific. End with what you learned or would do differently.

## Ready-Made STAR Examples

<!-- These are populated by /setup from your actual experience. Below are templates showing the format. -->

### 1. Illumina DRAGEN Pipeline Implementation (Technical Skills, Cloud Computing)
**S:** Genesis Genomics needed to migrate their variant analysis workflow from legacy tools to Illumina's DRAGEN server, improving speed and accuracy while reducing computational overhead.
**T:** As the R&D bioinformatics analyst, I was responsible for implementing, validating, and deploying the DRAGEN pipeline across both cloud (AWS) and on-premises infrastructure.
**A:** I studied DRAGEN's architecture, designed validation benchmarks against existing tools, deployed the pipeline using AWS services (S3, Lambda, Batch), and documented performance improvements. I also trained the operations team on usage and troubleshooting.
**R:** Successfully deployed DRAGEN across NovaSeq 6000 and NovaSeq X+ platforms, reducing variant calling time from hours to minutes while maintaining concordance with gold-standard pipelines. The solution is now the standard variant analysis path for clinical samples.
**Use for:** "Describe a technical project you led", "How do you approach learning new technologies?", "Tell me about a time you improved a process"

### 2. AWS Cloud Architecture for Genomics (Cloud Computing, Problem-Solving)
**S:** Genesis Genomics' on-premises storage was reaching capacity limits, and data transfer between laboratory instruments and analysis pipelines was becoming a bottleneck, especially with increasing sample throughput.
**T:** I was tasked with designing and deploying a cloud-based infrastructure on AWS to handle large-scale genomic data storage, transfer, and processing.
**A:** I architected a solution using S3 for scalable storage, DataSync for efficient data transfer, Lambda for event-driven processing, and IAM for security. I obtained my AWS Solutions Architect certification during this project and applied best practices for cost optimization.
**R:** Built a scalable cloud infrastructure that handles terabytes of genomic data monthly, reduced data transfer times by 60%, and established the foundation for future cloud-based bioinformatics services at the company.
**Use for:** "Tell me about a time you designed a system from scratch", "How do you handle large-scale data challenges?", "Describe your experience with cloud computing"

### 3. Oncology Translational Research - Mutational Profiling (Research, Communication)
**S:** As a PhD candidate at ICESP/FMUSP, I needed to characterize the somatic mutational landscape of high-grade serous ovarian carcinoma and triple-negative breast carcinoma in young versus elderly patients to identify potential therapeutic targets.
**T:** I was responsible for the entire research project: from sample processing and NGS library preparation to bioinformatics analysis, statistical interpretation, and manuscript preparation.
**A:** I performed NGS sequencing, developed custom bioinformatics pipelines for variant calling and annotation, performed statistical analysis using R, and collaborated with clinical teams to interpret findings. I also mentored junior researchers and presented results at international conferences.
**R:** Published findings in peer-reviewed journals (Cells, 2021; Oncotarget, 2018), contributing to the understanding of age-related mutational patterns in aggressive cancers. The research informed ongoing clinical trial designs at the institution.
**Use for:** "Tell me about your research experience", "How do you communicate complex findings?", "Describe a project where you worked independently"

### 4. Training and Knowledge Sharing (Leadership, Communication)
**S:** The bioinformatics team at ICESP was growing, and new members needed onboarding on NGS analysis pipelines and laboratory protocols to become productive quickly.
**T:** I was responsible for developing training materials and leading the VI Course in Molecular Oncology, as well as mentoring junior researchers in the lab.
**A:** I created comprehensive training documentation, developed hands-on exercises using real genomic datasets, delivered lectures on molecular oncology and bioinformatics, and established best practices for pipeline documentation.
**R:** Successfully onboarded multiple team members who became productive within weeks rather than months. The course I organized became an ongoing program at ICESP, and my documentation standards were adopted as lab-wide best practices.
**Use for:** "Tell me about a time you mentored someone", "How do you share knowledge with your team?", "Describe your leadership style"

### 5. Variant Analysis Platform Management (Adaptability, Operations)
**S:** Genesis Genomics uses multiple variant analysis platforms (Emedgene, Franklin, Varstation) for clinical interpretation, each with different interfaces, capabilities, and data formats, creating operational complexity.
**T:** I was responsible for administering these platforms, ensuring reliable operation for clinical workflows, and troubleshooting issues that arose during high-throughput sample processing.
**A:** I learned each platform deeply, developed standardized workflows for cross-platform validation, created troubleshooting guides, and built automation scripts to reduce manual intervention. I also worked closely with vendor support teams to resolve issues.
**R:** Achieved 99.9% platform uptime for clinical operations, reduced manual review time by 40% through automation, and established cross-platform concordance validation that caught potential discrepancies before clinical reporting.
**Use for:** "How do you handle multiple tools/systems?", "Tell me about a time you had to learn something quickly", "Describe how you ensure operational reliability"

## Common Tough Questions

### "Why did you leave [previous company]?"
> I'm not leaving Genesis Genomics because of dissatisfaction—I'm exploring opportunities that align more closely with my long-term goals in precision medicine and cloud-based bioinformatics. My current role has given me strong operational and R&D experience, and I'm now looking to apply those skills in a setting where I can contribute to larger-scale genomic data initiatives and continue growing architecturally.

### "You don't have [specific skill/experience]."
> While I may not have direct experience with [specific skill], my background in building and validating bioinformatics pipelines from scratch—combined with my AWS certification and hands-on cloud architecture work—demonstrates my ability to learn and apply new technologies quickly. For example, I self-studied for and passed the AWS Solutions Architect exam while working full-time, and I've consistently taken on new platform responsibilities at Genesis Genomics with minimal ramp-up time.

### "Where do you see yourself in 5 years?"
> In five years, I see myself in a senior bioinformatics or data engineering role where I'm designing end-to-end cloud-native solutions for genomic medicine—combining my domain expertise in oncology with my growing cloud and software engineering skills. I want to be leading technical initiatives that directly impact patient outcomes through precision medicine.

### "What's your biggest weakness?"
> I sometimes take on too much independently before asking for help, because I enjoy the problem-solving process. I've learned to recognize when this slows down the team, and I've gotten better at delegating and collaborating earlier in projects. For example, on the DRAGEN deployment, I made a conscious effort to involve the operations team from the start rather than building the solution in isolation.

### "Why this company specifically?"
> Customize per company. Must reference: specific projects, company values, market position, or team structure. Never give a generic answer.

## Questions You Should Ask Interviewers

### About the Role
- "What does a typical week look like in this role?"
- "What would success look like in the first 6 months?"
- "What's the biggest challenge the team is facing right now?"

### About the Team
- "How big is the team, and how do you divide work?"
- "What does the development/project lifecycle look like, from idea to production?"
- "How do you onboard new team members?"

### About Tech & Growth
- "What's your current tech stack for [relevant area]?"
- "Is there room to grow into more architectural or strategic decisions?"
- "How does the team stay current with new tools and methods?"

### About Culture (use these to prevent disappointment)
- "How would you describe the team culture?"
- "What does professional development look like here?"
- "Is there flexibility for remote/hybrid work?"
- "What's the balance between development/new projects and maintenance work?"
- "How would you describe the leadership style in this team?"
- "What do people who thrive here have in common?"

## Phone/Video Interview Tips
- Have STAR examples written out (use this file)
- Keep a glass of water nearby
- Smile when speaking (it changes your tone)
- Ask for clarification if a question is vague
- It's OK to take 5 seconds to think before answering
- End with: "Is there anything else you'd like to know about my background?"

## After the Application (Best Practice)

### Follow-Up Etiquette
- **Don't call to "stand out"** or to learn more about the role post-submission - this risks a negative impression
- If the employer specified a timeline, respect it and wait
- If no timeline was given and significant time has passed (2+ weeks), a brief call to ask about status is acceptable
- If you have genuinely new, relevant information to share, a short follow-up is fine

### Thank-You Notes
- When you receive any update (interview invitation, rejection, or status update), send a brief thank-you message
- Express appreciation for their time and the process
- Keep it short (2-3 sentences)

## Roleplay Guidelines
When the user asks for interview practice:
1. Ask which role/company to simulate
2. Start with easy warm-up questions ("Tell me about yourself")
3. Progress to role-specific technical questions
4. Include 1-2 behavioral questions using the competencies from the job posting
5. End with a tough question or curveball
6. After each answer, give brief feedback: what worked, what to sharpen
7. Suggest which STAR example would work best for each question
