# Guia de Seguranca Cloudflare - Ranking Run Pro

## 1. Cloudflare WAF (Web Application Firewall)
No painel Cloudflare do dominio `rankingrun.com.br`:
- **Security > WAF > Custom Rules**:
  - Regra 1: Bloquear requests sem `Referer` valido nas rotas `/api/ranking/` (exceto bots conhecidos)
  - Regra 2: Rate limit global: 300 req/min por IP (complementa o rate limit por usuario do backend)
  - Regra 3: Bloquear User-Agents de scrapers conhecidos (python-requests, scrapy, curl, wget)
  - Regra 4: Challenge para requests vindos de VPNs/datacenters (ASN filter)

## 2. Cloudflare Turnstile (CAPTCHA invisivel)
Para proteger formularios criticos:
- **Turnstile > Add Widget** no painel Cloudflare
- Obter `Site Key` e `Secret Key`
- Implementar no frontend (cadastro, login, votacao):
  ```html
  <div class="cf-turnstile" data-sitekey="SEU_SITE_KEY"></div>
  ```
- Validar no backend antes de processar a acao:
  ```python
  async def verify_turnstile(token: str) -> bool:
      async with httpx.AsyncClient() as client:
          resp = await client.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data={
              "secret": os.environ.get("TURNSTILE_SECRET"),
              "response": token
          })
          return resp.json().get("success", False)
  ```

## 3. Configuracoes Recomendadas no Cloudflare
- **SSL/TLS**: Full (Strict) - ja configurado
- **Speed > Optimization**: Auto Minify (JS, CSS, HTML)
- **Caching > Configuration**: Browser Cache TTL = 4h para assets estaticos
- **Security > Bot Fight Mode**: Ativar
- **Security > Challenge Passage**: 30 minutos

## 4. Headers Cloudflare
O backend ja esta preparado para ler `CF-Connecting-IP` quando necessario.
O rate limiting do backend usa User ID (JWT), nao IP, evitando falsos positivos.

## Prioridade de Implementacao
1. WAF Custom Rules (15 min no painel Cloudflare)
2. Bot Fight Mode (1 clique)
3. Turnstile no cadastro/login (opcional, requer codigo)
