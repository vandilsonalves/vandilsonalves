// Canvas Share Card Generator for Raio-X page
// Extracted from RaioXPage.jsx for maintainability
// Format: 9:16 (ideal for Instagram Stories)

const ICON_MAP_NAMES = {
  'trophy': 'Trophy', 'flame': 'Flame', 'target': 'Target', 'award': 'Award',
  'star': 'Star', 'zap': 'Zap', 'crown': 'Crown', 'medal': 'Medal',
  'shield': 'Shield', 'rocket': 'Rocket', 'heart': 'Heart', 'lightning': 'Lightning'
};

/**
 * Generate a 9:16 share card image using Canvas API
 * @param {Object} params - Parameters
 * @param {Object} params.data - Raio-X data
 * @param {Array} params.badges - User badges
 * @param {Object} params.atleta - Athlete profile data
 * @returns {Promise<string>} - Data URL of the generated image
 */
export const generateShareCardImage = async ({ data, badges, atleta }) => {
  try {
      // Extrair sub-objetos de data
      const score = data?.score || {};
      const evolucao = data?.evolucao || {};
      const records = data?.records || {};

      // Formato 9:16 para Stories (540x960)
      const width = 540;
      const height = 960;
      
      const canvas = document.createElement('canvas');
      canvas.width = width * 2; // Scale 2x para qualidade
      canvas.height = height * 2;
      const ctx = canvas.getContext('2d');
      
      // Scale para 2x
      ctx.scale(2, 2);
      
      // Background gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, '#0f172a');
      gradient.addColorStop(0.3, '#1e293b');
      gradient.addColorStop(0.7, '#1e293b');
      gradient.addColorStop(1, '#0f172a');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);
      
      // Decorative elements
      ctx.fillStyle = 'rgba(16, 185, 129, 0.1)';
      ctx.beginPath();
      ctx.arc(-50, 100, 200, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(width + 50, height - 100, 200, 0, Math.PI * 2);
      ctx.fill();
      
      let yPos = 30;
      
      // Header - Logo area
      const logoGradient = ctx.createLinearGradient(20, yPos, 68, yPos + 48);
      logoGradient.addColorStop(0, '#10b981');
      logoGradient.addColorStop(1, '#14b8a6');
      ctx.fillStyle = logoGradient;
      ctx.beginPath();
      ctx.roundRect(20, yPos, 48, 48, 12);
      ctx.fill();
      
      // Logo icon
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 26px Arial';
      ctx.fillText('⚡', 30, yPos + 35);
      
      // Title
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px Arial';
      ctx.fillText('RAIO-X do Atleta', 78, yPos + 25);
      ctx.fillStyle = '#10b981';
      ctx.font = '12px Arial';
      ctx.fillText('Ranking Run', 78, yPos + 42);
      
      // Website
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText('rankingrun.com.br', width - 20, yPos + 35);
      ctx.textAlign = 'left';
      
      yPos += 80;
      
      // Nome do atleta
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 26px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(atleta?.nome || 'Atleta', width / 2, yPos);
      if (atleta?.assessoria) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '13px Arial';
        ctx.fillText(atleta.assessoria, width / 2, yPos + 22);
        yPos += 30;
      }
      ctx.textAlign = 'left';
      
      yPos += 30;
      
      // Score circle (maior)
      const scoreValue = score.score_mes_atual || 0;
      const scoreX = width / 2;
      const scoreRadius = 60;
      
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 14;
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, 0, Math.PI * 2);
      ctx.stroke();
      
      // Score progress
      const scoreGradient = ctx.createLinearGradient(scoreX - scoreRadius, yPos, scoreX + scoreRadius, yPos + scoreRadius * 2);
      scoreGradient.addColorStop(0, '#10b981');
      scoreGradient.addColorStop(1, '#06b6d4');
      ctx.strokeStyle = scoreGradient;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, -Math.PI / 2, -Math.PI / 2 + (scoreValue / 100) * Math.PI * 2);
      ctx.stroke();
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`${scoreValue}%`, scoreX, yPos + scoreRadius + 12);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px Arial';
      ctx.fillText('Consistência', scoreX, yPos + scoreRadius + 32);
      ctx.textAlign = 'left';
      
      yPos += scoreRadius * 2 + 50;
      
      // Métricas em 2x2 grid
      const cardWidth = 240;
      const cardHeight = 75;
      const cardGap = 15;
      const gridStartX = (width - cardWidth * 2 - cardGap) / 2;
      
      const metrics = [
        { icon: '🏆', value: evolucao.totais?.total_provas || 0, label: 'Provas' },
        { icon: '📏', value: `${evolucao.totais?.distancia_total_km || 0} km`, label: 'Distância' },
        { icon: '⏱️', value: `${evolucao.totais?.tempo_total_horas || 0}h`, label: 'Tempo Total' },
        { icon: '⚡', value: records.records?.melhor_pace?.valor_formatado || '-', label: 'Melhor Pace' }
      ];
      
      metrics.forEach((metric, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const x = gridStartX + col * (cardWidth + cardGap);
        const y = yPos + row * (cardHeight + 10);
        
        // Card background
        ctx.fillStyle = 'rgba(71, 85, 105, 0.4)';
        ctx.beginPath();
        ctx.roundRect(x, y, cardWidth, cardHeight, 10);
        ctx.fill();
        
        // Icon
        ctx.font = '22px Arial';
        ctx.fillText(metric.icon, x + 15, y + 35);
        
        // Value
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 22px Arial';
        ctx.fillText(String(metric.value), x + 50, y + 35);
        
        // Label
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Arial';
        ctx.fillText(metric.label, x + 50, y + 55);
      });
      
      yPos += cardHeight * 2 + 40;
      
      // Records section
      ctx.fillStyle = 'rgba(71, 85, 105, 0.3)';
      ctx.beginPath();
      ctx.roundRect(20, yPos, width - 40, 90, 10);
      ctx.fill();
      
      ctx.fillStyle = '#facc15';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('🏅 Records Pessoais', 35, yPos + 25);
      
      const categories = ['5km', '10km', '21km', '42km'];
      const rpStartX = 35;
      const rpWidth = (width - 70) / 4;
      
      ctx.font = '11px Arial';
      categories.forEach((cat, i) => {
        const x = rpStartX + i * rpWidth;
        const rp = records.records?.por_categoria?.[cat];
        
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(cat, x, yPos + 50);
        
        ctx.fillStyle = rp ? '#10b981' : '#64748b';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(rp?.tempo || '-', x, yPos + 70);
        ctx.font = '11px Arial';
      });
      
      yPos += 110;
      
      // ========== INSÍGNIAS CONQUISTADAS ==========
      const badgesConquistados = badges.filter(b => b.conquistado);
      
      // Função para desenhar ícone do badge no Canvas (simplificada)
      const drawBadgeIcon = (ctx, icon, cx, cy, size) => {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        const s = size * 0.35;
        
        switch(icon) {
          case 'star':
            // Estrela de 5 pontas
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              const px = cx + r * Math.cos(angle);
              const py = cy + r * Math.sin(angle);
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'medal':
            // Medalha - círculo com fita
            ctx.beginPath();
            ctx.arc(cx, cy + s * 0.15, s * 0.65, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.35, cy - s * 0.5);
            ctx.lineTo(cx, cy - s * 0.1);
            ctx.lineTo(cx + s * 0.35, cy - s * 0.5);
            ctx.stroke();
            break;
            
          case 'trophy':
            // Troféu simplificado
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.4, cy - s * 0.4);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.15);
            ctx.lineTo(cx + s * 0.25, cy + s * 0.15);
            ctx.lineTo(cx + s * 0.4, cy - s * 0.4);
            ctx.closePath();
            ctx.fill();
            ctx.fillRect(cx - s * 0.15, cy + s * 0.15, s * 0.3, s * 0.25);
            ctx.fillRect(cx - s * 0.3, cy + s * 0.4, s * 0.6, s * 0.12);
            break;
            
          case 'award':
            // Prêmio/Roseta
            ctx.beginPath();
            ctx.arc(cx, cy - s * 0.1, s * 0.45, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.25, cy + s * 0.25);
            ctx.lineTo(cx - s * 0.4, cy + s * 0.65);
            ctx.lineTo(cx, cy + s * 0.35);
            ctx.lineTo(cx + s * 0.4, cy + s * 0.65);
            ctx.lineTo(cx + s * 0.25, cy + s * 0.25);
            ctx.fill();
            break;
            
          case 'zap':
            // Raio
            ctx.beginPath();
            ctx.moveTo(cx + s * 0.1, cy - s * 0.55);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.05);
            ctx.lineTo(cx + s * 0.05, cy + s * 0.05);
            ctx.lineTo(cx - s * 0.1, cy + s * 0.55);
            ctx.lineTo(cx + s * 0.25, cy - s * 0.05);
            ctx.lineTo(cx - s * 0.05, cy - s * 0.05);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'play':
            // Triângulo play
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.25, cy - s * 0.4);
            ctx.lineTo(cx + s * 0.4, cy);
            ctx.lineTo(cx - s * 0.25, cy + s * 0.4);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'shield':
            // Escudo
            ctx.beginPath();
            ctx.moveTo(cx, cy - s * 0.5);
            ctx.lineTo(cx + s * 0.45, cy - s * 0.25);
            ctx.lineTo(cx + s * 0.45, cy + s * 0.1);
            ctx.lineTo(cx, cy + s * 0.55);
            ctx.lineTo(cx - s * 0.45, cy + s * 0.1);
            ctx.lineTo(cx - s * 0.45, cy - s * 0.25);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'target':
            // Alvo - círculos concêntricos
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.5, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.3, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.12, 0, Math.PI * 2);
            ctx.fill();
            ctx.lineWidth = 2;
            break;
            
          case 'crown':
            // Coroa
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.45, cy + s * 0.25);
            ctx.lineTo(cx - s * 0.45, cy - s * 0.05);
            ctx.lineTo(cx - s * 0.2, cy + s * 0.1);
            ctx.lineTo(cx, cy - s * 0.4);
            ctx.lineTo(cx + s * 0.2, cy + s * 0.1);
            ctx.lineTo(cx + s * 0.45, cy - s * 0.05);
            ctx.lineTo(cx + s * 0.45, cy + s * 0.25);
            ctx.closePath();
            ctx.fill();
            break;
            
          case 'calendar':
            // Calendário
            ctx.fillRect(cx - s * 0.4, cy - s * 0.3, s * 0.8, s * 0.7);
            ctx.fillStyle = '#000000';
            ctx.fillRect(cx - s * 0.3, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx - s * 0.05, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx + s * 0.12, cy - s * 0.1, s * 0.18, s * 0.18);
            ctx.fillRect(cx - s * 0.3, cy + s * 0.15, s * 0.18, s * 0.18);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(cx - s * 0.25, cy - s * 0.5, s * 0.08, s * 0.2);
            ctx.fillRect(cx + s * 0.17, cy - s * 0.5, s * 0.08, s * 0.2);
            break;
            
          case 'users':
            // Pessoas
            ctx.beginPath();
            ctx.arc(cx - s * 0.18, cy - s * 0.2, s * 0.22, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx + s * 0.22, cy - s * 0.15, s * 0.18, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx - s * 0.18, cy + s * 0.35, s * 0.3, Math.PI, 0);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(cx + s * 0.22, cy + s * 0.3, s * 0.25, Math.PI, 0);
            ctx.fill();
            break;
            
          case 'flame':
            // Chama
            ctx.beginPath();
            ctx.moveTo(cx, cy - s * 0.5);
            ctx.quadraticCurveTo(cx + s * 0.45, cy - s * 0.15, cx + s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx + s * 0.12, cy + s * 0.5, cx, cy + s * 0.42);
            ctx.quadraticCurveTo(cx - s * 0.12, cy + s * 0.5, cx - s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx - s * 0.45, cy - s * 0.15, cx, cy - s * 0.5);
            ctx.fill();
            break;
            
          case 'sparkles':
            // Brilhos - estrelas pequenas
            const drawStar = (sx, sy, ss) => {
              ctx.beginPath();
              ctx.moveTo(sx, sy - ss);
              ctx.lineTo(sx + ss * 0.25, sy - ss * 0.25);
              ctx.lineTo(sx + ss, sy);
              ctx.lineTo(sx + ss * 0.25, sy + ss * 0.25);
              ctx.lineTo(sx, sy + ss);
              ctx.lineTo(sx - ss * 0.25, sy + ss * 0.25);
              ctx.lineTo(sx - ss, sy);
              ctx.lineTo(sx - ss * 0.25, sy - ss * 0.25);
              ctx.closePath();
              ctx.fill();
            };
            drawStar(cx - s * 0.2, cy - s * 0.2, s * 0.25);
            drawStar(cx + s * 0.22, cy + s * 0.08, s * 0.22);
            drawStar(cx - s * 0.08, cy + s * 0.32, s * 0.18);
            break;
            
          case 'eye':
            // Olho
            ctx.beginPath();
            ctx.moveTo(cx - s * 0.5, cy);
            ctx.quadraticCurveTo(cx, cy - s * 0.35, cx + s * 0.5, cy);
            ctx.quadraticCurveTo(cx, cy + s * 0.35, cx - s * 0.5, cy);
            ctx.fill();
            ctx.fillStyle = '#000000';
            ctx.beginPath();
            ctx.arc(cx, cy, s * 0.18, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(cx - s * 0.05, cy - s * 0.05, s * 0.07, 0, Math.PI * 2);
            ctx.fill();
            break;
            
          default:
            // Ícone padrão - estrela
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              const px = cx + r * Math.cos(angle);
              const py = cy + r * Math.sin(angle);
              if (i === 0) ctx.moveTo(px, py);
              else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.fill();
        }
      };
      
      if (badgesConquistados.length > 0) {
        // Calcular altura necessária
        const badgeSize = 52;
        const badgeGap = 10;
        const maxBadgesPerRow = 7;
        const numRows = Math.min(Math.ceil(badgesConquistados.length / maxBadgesPerRow), 2);
        const sectionHeight = 55 + numRows * (badgeSize + 12);
        
        // Fundo da seção
        ctx.fillStyle = 'rgba(234, 179, 8, 0.15)';
        ctx.beginPath();
        ctx.moveTo(30, yPos);
        ctx.lineTo(width - 30, yPos);
        ctx.lineTo(width - 20, yPos + 10);
        ctx.lineTo(width - 20, yPos + sectionHeight - 10);
        ctx.lineTo(width - 30, yPos + sectionHeight);
        ctx.lineTo(30, yPos + sectionHeight);
        ctx.lineTo(20, yPos + sectionHeight - 10);
        ctx.lineTo(20, yPos + 10);
        ctx.closePath();
        ctx.fill();
        
        ctx.fillStyle = '#facc15';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`🎖️ Insígnias Conquistadas (${badgesConquistados.length})`, 35, yPos + 25);
        
        // Desenhar insígnias
        const badgesToShow = badgesConquistados.slice(0, maxBadgesPerRow * 2);
        const badgesInFirstRow = Math.min(badgesToShow.length, maxBadgesPerRow);
        const totalBadgesWidth = badgesInFirstRow * (badgeSize + badgeGap) - badgeGap;
        const badgeStartX = (width - totalBadgesWidth) / 2;
        
        badgesToShow.forEach((badge, i) => {
          const row = Math.floor(i / maxBadgesPerRow);
          const col = i % maxBadgesPerRow;
          
          const badgesInThisRow = row === 0 ? badgesInFirstRow : Math.min(badgesToShow.length - maxBadgesPerRow, maxBadgesPerRow);
          const rowWidth = badgesInThisRow * (badgeSize + badgeGap) - badgeGap;
          const rowStartX = (width - rowWidth) / 2;
          
          const x = rowStartX + col * (badgeSize + badgeGap);
          const y = yPos + 40 + row * (badgeSize + 14);
          const cx = x + badgeSize / 2;
          const cy = y + badgeSize / 2;
          
          // Sombra
          ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
          ctx.beginPath();
          ctx.arc(cx + 2, cy + 3, badgeSize / 2.3, 0, Math.PI * 2);
          ctx.fill();
          
          // Badge circular com gradiente
          const corPrimaria = badge.cor_primaria || '#10b981';
          const corSecundaria = badge.cor_secundaria || '#059669';
          const badgeGradient = ctx.createRadialGradient(cx - 5, cy - 5, 0, cx, cy, badgeSize / 2);
          badgeGradient.addColorStop(0, corPrimaria);
          badgeGradient.addColorStop(1, corSecundaria);
          ctx.fillStyle = badgeGradient;
          
          ctx.beginPath();
          ctx.arc(cx, cy, badgeSize / 2 - 2, 0, Math.PI * 2);
          ctx.fill();
          
          // Borda brilhante
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
          ctx.lineWidth = 2;
          ctx.stroke();
          
          // Brilho no topo
          ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
          ctx.beginPath();
          ctx.arc(cx - 3, cy - badgeSize / 5, badgeSize / 5, 0, Math.PI * 2);
          ctx.fill();
          
          // Desenhar o ícone
          drawBadgeIcon(ctx, badge.icone, cx, cy, badgeSize);
        });
        
        yPos += sectionHeight + 15;
      }
      
      // Footer (posicionado no final)
      const footerY = Math.max(yPos, height - 50);
      
      // Linha decorativa
      const lineGradient = ctx.createLinearGradient(20, footerY, width - 20, footerY);
      lineGradient.addColorStop(0, '#10b981');
      lineGradient.addColorStop(0.5, '#06b6d4');
      lineGradient.addColorStop(1, '#10b981');
      ctx.strokeStyle = lineGradient;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(20, footerY);
      ctx.lineTo(width - 20, footerY);
      ctx.stroke();
      
      ctx.fillStyle = '#64748b';
      ctx.font = '11px Arial';
      ctx.fillText(`Gerado em ${new Date().toLocaleDateString('pt-BR')}`, 20, footerY + 25);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 12px Arial';
      ctx.fillText('Ranking Run', width - 20, footerY + 25);
      ctx.textAlign = 'left';

      const imageUrl = canvas.toDataURL('image/png');
      return imageUrl;
    } catch (error) {
      console.error('Erro ao gerar card:', error);
      throw error;
    }
};
