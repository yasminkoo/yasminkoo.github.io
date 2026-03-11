#!/usr/bin/env python3
import http.server
import os

class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404)
            return None

        fs = os.fstat(f.fileno())
        file_len = fs[6]
        ctype = self.guess_type(path)

        range_header = self.headers.get('Range')
        if range_header:
            try:
                ranges = range_header.strip().replace('bytes=', '').split('-')
                start = int(ranges[0]) if ranges[0] else 0
                end = int(ranges[1]) if ranges[1] else file_len - 1
                end = min(end, file_len - 1)
                length = end - start + 1
                f.seek(start)
                self.send_response(206)
                self.send_header('Content-type', ctype)
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_len}')
                self.send_header('Content-Length', str(length))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                return f
            except Exception:
                pass

        self.send_response(200)
        self.send_header('Content-type', ctype)
        self.send_header('Content-Length', str(file_len))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        return f

if __name__ == '__main__':
    import sys
    from socketserver import ThreadingMixIn
    class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with ThreadedHTTPServer(('', port), RangeHTTPRequestHandler) as httpd:
        print(f'Serving on http://localhost:{port}')
        httpd.serve_forever()
