# PRD - Ranking Run Pro

## Problema Original
Plataforma de ranking de corridas completa com sistema de ranking profissional/amador, feed social, stories, sistema de mensagens admin, Raio-X do atleta, integracoes com Strava e sistema de monetizacao via Stripe.

## Arquitetura
- **Frontend**: React + TailwindCSS + Shadcn UI
- **Backend**: FastAPI + MongoDB (Motor)
- **Pagamentos**: Stripe (via emergentintegrations)

## Funcionalidades Implementadas

### Sistema de Pagamento
- [x] Plano Lancamento: R$97 (de R$197) ate 14/12/2026
- [x] Plano Anual: 12x R$119 a partir de 15/12/2026
- [x] Checkout Stripe + Webhook + Polling + Banner contagem regressiva

### Bloqueio de Acesso Expirados
- [x] require_premium_access + AccessGate + PrintProtection

### Mobile Responsiveness (25-26/03/2026)
- [x] MobileNav drawer lateral (hamburger menu)
- [x] Header mobile compacto em todas as paginas
- [x] Grid 2x2 ranking + botoes compactos
- [x] Sidebar Assessoria responsiva com drawer
- [x] Share card: crossOrigin, scale 3, foto corrigida, ano 2026
- [x] overflow-x: hidden global (App.css)
- [x] Headers responsivos: RaioX, Perfil, Corridas, Submeter
- [x] Campo upload de foto compacto no mobile (Submeter)

## Credenciais
- Admin: admin@runpro.com / admin
- Atleta (teste): teste.dono@teste.com / 123456
- Atleta (expirado): expirado@teste.com / 123456

## Backlog
- P2: Exportar Raio-X como PDF
- P3: Notificacoes push por email (Resend)

## Issues Conhecidas
- Redis instavel (restarts manuais)
