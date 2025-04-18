import fs from "fs";

export async function POST(req) {
  try {
    console.log("API called");

    const { path: inputPath } = await req.json();
    console.log("Path received:", inputPath);

    // Check if the path exists
    const exists = fs.existsSync(inputPath);
    console.log("Path exists:", exists);

    return new Response(JSON.stringify({ exists }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in /api/check-path:", error);
    return new Response(
      JSON.stringify({ error: "Failed to check the path." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
} 