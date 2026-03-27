import { redirect } from "next/navigation";

// /upload is no longer a separate page — everything is on the home page
export default function UploadPage() {
  redirect("/");
}
