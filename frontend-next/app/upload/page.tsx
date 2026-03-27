import Navbar from "@/components/Navbar";
import CsvUpload from "@/components/CsvUpload";

export default function UploadPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar role="Admin" />
      <div className="max-w-xl mx-auto px-6 py-12">
        <h1 className="text-2xl font-bold mb-1 text-white">Upload CSV Data</h1>
        <p className="text-slate-400 text-sm mb-8">
          Upload a CSV file to automatically create a queryable table in the database.
        </p>
        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-lg">
          <CsvUpload />
        </div>
        <p className="text-xs text-slate-600 mt-4 text-center">
          Supported: CSV files up to 50 MB. Table names are auto-sanitized.
        </p>
      </div>
    </div>
  );
}
