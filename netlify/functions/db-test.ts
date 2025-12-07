import { Context } from "@netlify/functions";
import { neon, NeonQueryFunction } from "@netlify/neon";

// Connection pooling: reuse the database connection across invocations
let cachedSql: NeonQueryFunction<false, false> | null = null;

function getSql(): NeonQueryFunction<false, false> {
  if (!cachedSql) {
    cachedSql = neon();
  }
  return cachedSql;
}

// Simple in-memory rate limiter (for production, consider Redis or similar)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

function checkRateLimit(ip: string, maxRequests = 60, windowMs = 60000): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(ip);
  
  // Clean up old entries periodically to prevent memory leaks
  if (rateLimitMap.size > 10000) {
    const cutoff = now - windowMs;
    for (const [key, value] of rateLimitMap.entries()) {
      if (value.resetTime < cutoff) {
        rateLimitMap.delete(key);
      }
    }
  }
  
  if (!record || now > record.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + windowMs });
    return true;
  }
  
  if (record.count < maxRequests) {
    record.count++;
    return true;
  }
  
  return false;
}

export default async (req: Request, context: Context) => {
  const startTime = performance.now();
  
  // Validate HTTP method
  if (req.method !== 'GET') {
    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      {
        status: 405,
        headers: {
          "Content-Type": "application/json",
          "Allow": "GET",
        },
      }
    );
  }
  
  // Rate limiting
  const clientIp = context.ip || 'unknown';
  if (!checkRateLimit(clientIp)) {
    return new Response(
      JSON.stringify({ 
        error: "Rate limit exceeded",
        message: "Too many requests. Please try again later."
      }),
      {
        status: 429,
        headers: {
          "Content-Type": "application/json",
          "Retry-After": "60",
          "X-RateLimit-Limit": "60",
          "X-RateLimit-Remaining": "0",
          "X-RateLimit-Reset": String(Math.floor(Date.now() / 1000) + 60),
        },
      }
    );
  }
  
  try {
    // Use cached connection for better performance
    const _sql = getSql();

    // Parse and validate query parameters
    const url = new URL(req.url);
    const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') || '10'), 1), 100);

    // Example query - adjust based on your schema
    // const result = await sql`SELECT * FROM coins LIMIT ${limit}`;

    const responseTime = performance.now() - startTime;
    
    // Get rate limit info for headers
    const record = rateLimitMap.get(clientIp);
    const remaining = record ? Math.max(60 - record.count, 0) : 59;

    return new Response(
      JSON.stringify({
        message: "Database connection available",
        timestamp: new Date().toISOString(),
        responseTime: `${responseTime.toFixed(2)}ms`,
        limit,
        // data: result,
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "public, max-age=60", // Cache for 60 seconds
          "X-RateLimit-Limit": "60",
          "X-RateLimit-Remaining": String(remaining),
          "X-RateLimit-Reset": String(Math.floor(Date.now() / 1000) + 60),
        },
      }
    );
  } catch (error) {
    const responseTime = performance.now() - startTime;
    
    // Log detailed error information for debugging
    const errorDetails = {
      message: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: new Date().toISOString(),
      responseTime: `${responseTime.toFixed(2)}ms`,
      ip: clientIp,
    };
    
    console.error("Database error:", errorDetails);
    
    return new Response(
      JSON.stringify({
        error: "Database connection failed",
        message: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
  }
};
