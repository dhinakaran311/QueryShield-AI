import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 180000,
});

export interface GenerateSqlResponse {
  success: boolean;
  question: string;
  sql: string;
  is_followup: boolean;
  schema_used: string[];
}

export interface ExecuteSqlResponse {
  success: boolean;
  data: Record<string, unknown>[];
  columns: string[];
  count: number;
  was_corrected: boolean;
  corrected_sql?: string;
  query_cost: number;
  cost_level: string;
  cost_label: string;
  was_optimized: boolean;
  message?: string;
}

export interface UploadCsvResponse {
  success: boolean;
  message: string;
  table_name: string;
  rows_inserted: number;
  columns: string[];
  schema: Record<string, string>;
}

export const generateSql = (
  question: string,
  lastNl: string | null,
  lastSql: string | null,
  role: string
) =>
  API.post<GenerateSqlResponse>("/generate-sql", {
    question,
    last_nl: lastNl,
    last_sql: lastSql,
    role,
  });

export const executeSql = (question: string, sql: string, role: string) =>
  API.post<ExecuteSqlResponse>("/execute-sql", {
    question,
    last_sql: sql,
    role,
  });

export const uploadCsv = (
  file: File,
  tableName: string,
  uploadedBy: string
) => {
  const form = new FormData();
  form.append("file", file);
  form.append("table_name", tableName);
  form.append("uploaded_by", uploadedBy);
  return API.post<UploadCsvResponse>("/upload-csv", form);
};

export const getSchema = () => API.get("/schema");
export const getHealth = () => API.get("/health");
