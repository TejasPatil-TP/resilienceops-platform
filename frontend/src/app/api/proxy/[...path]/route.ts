import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, (await params).path);
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, (await params).path);
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, (await params).path);
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, (await params).path);
}

const ALLOWED_ENDPOINTS: Record<string, string[]> = {
  'services': ['GET', 'POST'],
  'slos': ['GET', 'POST'],
  'alerts': ['GET', 'POST', 'PUT'],
  'experiments': ['GET', 'POST', 'DELETE'],
  'overview': ['GET'],
};

async function proxyRequest(request: NextRequest, pathArray: string[]) {
  const isProduction = process.env.NODE_ENV === 'production';
  
  const backendUrlStr = process.env.API_BASE_URL || (isProduction ? '' : 'http://localhost:8000/api/v1');
  const demoApiKey = process.env.DEMO_API_KEY || (isProduction ? '' : 'dev-demo-key');

  if (isProduction && (!backendUrlStr || !demoApiKey)) {
    return NextResponse.json({ error: 'Server configuration missing' }, { status: 500 });
  }

  let backendUrl: URL;
  try {
    backendUrl = new URL(backendUrlStr);
    // Explicit HTTPS requirement in production unless bypassed via flag
    if (isProduction && backendUrl.protocol !== 'https:' && process.env.ALLOW_INSECURE_INTERNAL_API !== 'true') {
        return NextResponse.json({ error: 'HTTPS required for API upstream' }, { status: 500 });
    }
    if (backendUrl.protocol !== 'http:' && backendUrl.protocol !== 'https:') {
      throw new Error('Invalid scheme');
    }
    
    // Trusted Upstream check
    const allowedUpstreams = process.env.ALLOWED_UPSTREAMS ? process.env.ALLOWED_UPSTREAMS.split(',') : [];
    if (isProduction && allowedUpstreams.length > 0 && !allowedUpstreams.includes(backendUrl.host)) {
        return NextResponse.json({ error: 'Upstream host not allowed' }, { status: 500 });
    }
  } catch (e) {
    return NextResponse.json({ error: 'Invalid backend configuration' }, { status: 500 });
  }

  if (!pathArray || pathArray.length === 0) {
    return NextResponse.json({ error: 'Invalid path' }, { status: 400 });
  }
  
  for (const segment of pathArray) {
    if (segment === '..' || segment === '.' || decodeURIComponent(segment).includes('..')) {
      return NextResponse.json({ error: 'Path traversal detected' }, { status: 400 });
    }
  }

  const rootResource = pathArray[0];
  const allowedMethods = ALLOWED_ENDPOINTS[rootResource];
  if (!allowedMethods) {
    return NextResponse.json({ error: 'Resource not allowed' }, { status: 403 });
  }
  
  if (!allowedMethods.includes(request.method)) {
    return NextResponse.json({ error: 'Method not allowed for this resource' }, { status: 405 });
  }

  const pathString = pathArray.map(encodeURIComponent).join('/');
  
  const sessionCookie = request.cookies.get('session');
  let token = sessionCookie?.value;
  if (!token) {
    if (isProduction) {
      return NextResponse.json({ error: 'Unauthorized. No session cookie.' }, { status: 401 });
    }
    token = 'dev-token';
  }

  const url = new URL(request.url);
  const targetUrl = new URL(
    backendUrl.pathname.endsWith('/') 
      ? backendUrl.pathname + pathString 
      : backendUrl.pathname + '/' + pathString, 
    backendUrl.origin
  );
  targetUrl.search = url.search;

  // Stream body reading to enforce byte limit safely without relying on Content-Length
  let bodyBuffer: Uint8Array | undefined = undefined;
  if (request.method !== 'GET' && request.method !== 'HEAD' && request.body) {
      const reader = request.body.getReader();
      const chunks: Uint8Array[] = [];
      let totalBytes = 0;
      const MAX_BYTES = 1048576; // 1MB

      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          if (value) {
              totalBytes += value.byteLength;
              if (totalBytes > MAX_BYTES) {
                  return NextResponse.json({ error: 'Payload too large' }, { status: 413 });
              }
              chunks.push(value);
          }
      }
      
      bodyBuffer = new Uint8Array(totalBytes);
      let offset = 0;
      for (const chunk of chunks) {
          bodyBuffer.set(chunk, offset);
          offset += chunk.length;
      }
  }

  const outgoingHeaders = new Headers();
  outgoingHeaders.set('Authorization', 'Bearer ' + token);
  outgoingHeaders.set('X-API-Key', demoApiKey);
  
  const incomingContentType = request.headers.get('content-type');
  if (incomingContentType) {
    outgoingHeaders.set('Content-Type', incomingContentType);
  }
  outgoingHeaders.set('Accept', 'application/json');

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(targetUrl.toString(), {
      method: request.method,
      headers: outgoingHeaders,
      body: bodyBuffer ? (bodyBuffer.buffer as ArrayBuffer) : undefined,
      redirect: 'error',
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    const responseData = await response.text();
    
    const returnHeaders = new Headers();
    const contentType = response.headers.get('Content-Type');
    if (contentType) returnHeaders.set('Content-Type', contentType);

    if (!response.ok) {
      try {
        const jsonError = JSON.parse(responseData);
        if (jsonError.detail && typeof jsonError.detail === 'string' && jsonError.detail.includes('Traceback')) {
           return NextResponse.json({ error: 'Internal Server Error' }, { status: 500, headers: returnHeaders });
        }
      } catch (e) {}
    }

    return new NextResponse(responseData, {
      status: response.status,
      headers: returnHeaders,
    });
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json({ error: 'Upstream timeout' }, { status: 504 });
    }
    console.error('Proxy error occurred (hidden from client)');
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}




