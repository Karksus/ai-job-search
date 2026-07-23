export interface JobCard {
  id: string;
  title: string;
  company: string;
  location: string;
  date: string;
  url: string;
  remote: boolean;
  salary: string | null;
  tags: string[];
}

export interface JobDetail extends JobCard {
  description: string;
  seniority: string;
  employmentType: string;
  jobFunction: string;
  industries: string[];
}

export interface SearchEnvelope {
  meta: { count: number; page: number; total?: number };
  results: JobCard[];
}
