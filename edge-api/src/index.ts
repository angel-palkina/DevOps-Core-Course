export interface Env {
  APP_NAME: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({ status: "ok" });
    }

    if (url.pathname === "/") {
      return Response.json({
        app: env.APP_NAME,
        message: "Hello from Cloudflare Workers",
        timestamp: new Date().toISOString(),
      });
    }

    if (url.pathname === "/edge") {
      return Response.json({
        colo: request.cf?.colo,
        country: request.cf?.country,
        city: request.cf?.city,
        asn: request.cf?.asn,
        httpProtocol: request.cf?.httpProtocol,
        tlsVersion: request.cf?.tlsVersion,
      });
    }

    return new Response("Not Found", { status: 404 });
  },
};