import Navbar from "@/components/Navbar";
import CsvUpload from "@/components/CsvUpload";

export default function UploadPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar role="Admin" />
      <div className="max-w-2xl mx-auto px-6 py-12">
        <h1 className="text-2xl font-bold mb-2">Upload CSV Data</h1>
        <p className="text-slate-400 text-sm mb-8">
          Upload a CSV file to automatically create a queryable table in the database.
        </p>
        <CsvUpload />
      </div>
    </div>
  );
}
