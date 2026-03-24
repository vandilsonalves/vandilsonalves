// Canvas Share Card Generator for Raio-X page
// Format: 9:16 (ideal for Instagram Stories)

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
      const comparativo = data?.comparativo || {};
      const previsoes = data?.previsoes || {};

      // Formato 9:16 para Stories (540x1200 - mais espaço para dados)
      const width = 540;
      const height = 1200;
      
      const canvas = document.createElement('canvas');
      canvas.width = width * 2;
      canvas.height = height * 2;
      const ctx = canvas.getContext('2d');
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
      ctx.fillStyle = 'rgba(16, 185, 129, 0.08)';
      ctx.beginPath();
      ctx.arc(-50, 100, 200, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(width + 50, height - 100, 200, 0, Math.PI * 2);
      ctx.fill();
      
      let yPos = 25;
      
      // ========== HEADER ==========
      const logoGradient = ctx.createLinearGradient(20, yPos, 68, yPos + 44);
      logoGradient.addColorStop(0, '#10b981');
      logoGradient.addColorStop(1, '#14b8a6');
      ctx.fillStyle = logoGradient;
      ctx.beginPath();
      ctx.roundRect(20, yPos, 44, 44, 10);
      ctx.fill();
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 24px Arial';
      ctx.fillText('\u26A1', 28, yPos + 32);
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 16px Arial';
      ctx.fillText('RAIO-X do Atleta', 74, yPos + 22);
      ctx.fillStyle = '#10b981';
      ctx.font = '11px Arial';
      ctx.fillText('Ranking Run', 74, yPos + 38);
      
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText('rankingrun.com.br', width - 20, yPos + 32);
      ctx.textAlign = 'left';
      
      yPos += 65;
      
      // ========== NOME DO ATLETA ==========
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 22px Arial';
      ctx.textAlign = 'center';
      const nome = atleta?.nome || 'Atleta';
      ctx.fillText(nome.length > 28 ? nome.substring(0, 28) + '...' : nome, width / 2, yPos);
      if (atleta?.assessoria) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '12px Arial';
        ctx.fillText(atleta.assessoria, width / 2, yPos + 18);
        yPos += 20;
      }
      if (atleta?.cidade && atleta?.estado) {
        ctx.fillStyle = '#64748b';
        ctx.font = '11px Arial';
        ctx.fillText(`${atleta.cidade} - ${atleta.estado}`, width / 2, yPos + 18);
        yPos += 20;
      }
      ctx.textAlign = 'left';
      
      yPos += 20;
      
      // ========== SCORE CIRCLE ==========
      const scoreValue = score.score_mes_atual || 0;
      const scoreX = width / 2;
      const scoreRadius = 50;
      
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 12;
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, 0, Math.PI * 2);
      ctx.stroke();
      
      const scoreGradient = ctx.createLinearGradient(scoreX - scoreRadius, yPos, scoreX + scoreRadius, yPos + scoreRadius * 2);
      scoreGradient.addColorStop(0, '#10b981');
      scoreGradient.addColorStop(1, '#06b6d4');
      ctx.strokeStyle = scoreGradient;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(scoreX, yPos + scoreRadius, scoreRadius, -Math.PI / 2, -Math.PI / 2 + (scoreValue / 100) * Math.PI * 2);
      ctx.stroke();
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 30px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`${scoreValue}%`, scoreX, yPos + scoreRadius + 10);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px Arial';
      ctx.fillText('Consistencia', scoreX, yPos + scoreRadius + 26);
      ctx.textAlign = 'left';
      
      yPos += scoreRadius * 2 + 40;
      
      // ========== METRICAS 2x2 ==========
      const cardWidth = 235;
      const cardHeight = 65;
      const cardGap = 12;
      const gridStartX = (width - cardWidth * 2 - cardGap) / 2;
      
      const metrics = [
        { icon: '\uD83C\uDFC6', value: evolucao.totais?.total_provas || 0, label: 'Provas' },
        { icon: '\uD83D\uDCCF', value: `${evolucao.totais?.distancia_total_km || 0} km`, label: 'Distancia' },
        { icon: '\u23F1\uFE0F', value: `${evolucao.totais?.tempo_total_horas || 0}h`, label: 'Tempo Total' },
        { icon: '\u26A1', value: records.records?.melhor_pace?.valor_formatado || '-', label: 'Melhor Pace' }
      ];
      
      metrics.forEach((metric, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const x = gridStartX + col * (cardWidth + cardGap);
        const y = yPos + row * (cardHeight + 8);
        
        ctx.fillStyle = 'rgba(71, 85, 105, 0.4)';
        ctx.beginPath();
        ctx.roundRect(x, y, cardWidth, cardHeight, 8);
        ctx.fill();
        
        ctx.font = '20px Arial';
        ctx.fillText(metric.icon, x + 12, y + 32);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 20px Arial';
        ctx.fillText(String(metric.value), x + 42, y + 32);
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px Arial';
        ctx.fillText(metric.label, x + 42, y + 48);
      });
      
      yPos += (cardHeight + 8) * 2 + 20;
      
      // ========== EVOLUCAO - Mini Bar Chart ==========
      const evolucaoMensal = evolucao.mensal || [];
      if (evolucaoMensal.length > 0) {
        ctx.fillStyle = 'rgba(71, 85, 105, 0.25)';
        ctx.beginPath();
        ctx.roundRect(20, yPos, width - 40, 120, 10);
        ctx.fill();
        
        ctx.fillStyle = '#3b82f6';
        ctx.font = 'bold 12px Arial';
        ctx.fillText('\uD83D\uDCC8 Evolucao Mensal', 35, yPos + 20);
        
        const chartX = 35;
        const chartY = yPos + 32;
        const chartW = width - 70;
        const chartH = 70;
        const last6 = evolucaoMensal.slice(-6);
        const maxDist = Math.max(...last6.map(m => m.distancia_km || m.distancia || 0), 1);
        const barW = Math.min(30, (chartW / last6.length) - 6);
        
        last6.forEach((mes, i) => {
          const dist = mes.distancia_km || mes.distancia || 0;
          const barH = (dist / maxDist) * chartH;
          const bx = chartX + i * (chartW / last6.length) + (chartW / last6.length - barW) / 2;
          const by = chartY + chartH - barH;
          
          const barGrad = ctx.createLinearGradient(bx, by, bx, by + barH);
          barGrad.addColorStop(0, '#3b82f6');
          barGrad.addColorStop(1, '#1d4ed8');
          ctx.fillStyle = barGrad;
          ctx.beginPath();
          ctx.roundRect(bx, by, barW, barH, 3);
          ctx.fill();
          
          ctx.fillStyle = '#94a3b8';
          ctx.font = '9px Arial';
          ctx.textAlign = 'center';
          const mesLabel = mes.mes || mes.label || `M${i+1}`;
          ctx.fillText(typeof mesLabel === 'string' ? mesLabel.substring(0, 3) : `M${i+1}`, bx + barW / 2, chartY + chartH + 12);
          
          if (dist > 0) {
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 9px Arial';
            ctx.fillText(`${Math.round(dist)}`, bx + barW / 2, by - 4);
          }
          ctx.textAlign = 'left';
        });
        
        yPos += 135;
      }
      
      // ========== RECORDS PESSOAIS ==========
      ctx.fillStyle = 'rgba(71, 85, 105, 0.25)';
      ctx.beginPath();
      ctx.roundRect(20, yPos, width - 40, 80, 10);
      ctx.fill();
      
      ctx.fillStyle = '#facc15';
      ctx.font = 'bold 12px Arial';
      ctx.fillText('\uD83C\uDFC5 Records Pessoais', 35, yPos + 20);
      
      const categories = ['5km', '10km', '21km', '42km'];
      const rpStartX = 35;
      const rpWidth = (width - 70) / 4;
      
      categories.forEach((cat, i) => {
        const x = rpStartX + i * rpWidth;
        const rp = records.records?.por_categoria?.[cat];
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Arial';
        ctx.fillText(cat, x, yPos + 42);
        
        ctx.fillStyle = rp ? '#10b981' : '#64748b';
        ctx.font = 'bold 13px Arial';
        ctx.fillText(rp?.tempo || '-', x, yPos + 60);
      });
      
      yPos += 95;
      
      // ========== COMPARATIVO ==========
      const compMedia = comparativo.media_geral;
      if (compMedia) {
        ctx.fillStyle = 'rgba(71, 85, 105, 0.25)';
        ctx.beginPath();
        ctx.roundRect(20, yPos, width - 40, 85, 10);
        ctx.fill();
        
        ctx.fillStyle = '#8b5cf6';
        ctx.font = 'bold 12px Arial';
        ctx.fillText('\uD83D\uDCCA Comparativo vs Media', 35, yPos + 20);
        
        const compItems = [
          { label: 'Pace', voce: comparativo.atleta?.pace_medio || '-', media: compMedia.pace_medio || '-' },
          { label: 'Provas', voce: comparativo.atleta?.total_provas || 0, media: Math.round(compMedia.total_provas || 0) },
          { label: 'Km/mes', voce: Math.round(comparativo.atleta?.km_mes || 0), media: Math.round(compMedia.km_mes || 0) }
        ];
        
        const compW = (width - 70) / 3;
        compItems.forEach((item, i) => {
          const x = 35 + i * compW;
          ctx.fillStyle = '#94a3b8';
          ctx.font = '10px Arial';
          ctx.fillText(item.label, x, yPos + 38);
          
          ctx.fillStyle = '#10b981';
          ctx.font = 'bold 12px Arial';
          ctx.fillText(`Voce: ${item.voce}`, x, yPos + 54);
          
          ctx.fillStyle = '#64748b';
          ctx.font = '11px Arial';
          ctx.fillText(`Media: ${item.media}`, x, yPos + 68);
        });
        
        yPos += 100;
      }
      
      // ========== PREVISOES IA ==========
      if (previsoes && (previsoes.proximo_pace || previsoes.proxima_meta)) {
        ctx.fillStyle = 'rgba(16, 185, 129, 0.1)';
        ctx.beginPath();
        ctx.roundRect(20, yPos, width - 40, 50, 10);
        ctx.fill();
        
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();
        
        ctx.fillStyle = '#10b981';
        ctx.font = 'bold 11px Arial';
        ctx.fillText('\uD83E\uDD16 Previsao IA', 35, yPos + 18);
        
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '11px Arial';
        const prevText = previsoes.proximo_pace 
          ? `Proximo pace estimado: ${previsoes.proximo_pace}`
          : `Proxima meta: ${previsoes.proxima_meta}`;
        ctx.fillText(prevText.length > 55 ? prevText.substring(0, 55) + '...' : prevText, 35, yPos + 36);
        
        yPos += 60;
      }
      
      // ========== INSIGNIAS CONQUISTADAS ==========
      const badgesConquistados = badges.filter(b => b.conquistado);
      
      const drawBadgeIcon = (ctx, icon, cx, cy, size) => {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        const s = size * 0.35;
        
        switch(icon) {
          case 'star':
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
            }
            ctx.closePath();
            ctx.fill();
            break;
          case 'trophy':
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
          case 'zap':
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
          case 'flame':
            ctx.beginPath();
            ctx.moveTo(cx, cy - s * 0.5);
            ctx.quadraticCurveTo(cx + s * 0.45, cy - s * 0.15, cx + s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx + s * 0.12, cy + s * 0.5, cx, cy + s * 0.42);
            ctx.quadraticCurveTo(cx - s * 0.12, cy + s * 0.5, cx - s * 0.28, cy + s * 0.35);
            ctx.quadraticCurveTo(cx - s * 0.45, cy - s * 0.15, cx, cy - s * 0.5);
            ctx.fill();
            break;
          case 'shield':
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
          case 'crown':
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
          case 'target':
            ctx.lineWidth = 3;
            ctx.beginPath(); ctx.arc(cx, cy, s * 0.5, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(cx, cy, s * 0.3, 0, Math.PI * 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(cx, cy, s * 0.12, 0, Math.PI * 2); ctx.fill();
            ctx.lineWidth = 2;
            break;
          default:
            ctx.beginPath();
            for (let i = 0; i < 10; i++) {
              const angle = (i * Math.PI / 5) - Math.PI / 2;
              const r = i % 2 === 0 ? s : s * 0.5;
              ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
            }
            ctx.closePath();
            ctx.fill();
        }
      };
      
      if (badgesConquistados.length > 0) {
        const badgeSize = 46;
        const badgeGap = 8;
        const maxBadgesPerRow = 7;
        const numRows = Math.min(Math.ceil(badgesConquistados.length / maxBadgesPerRow), 2);
        const sectionHeight = 48 + numRows * (badgeSize + 10);
        
        ctx.fillStyle = 'rgba(234, 179, 8, 0.12)';
        ctx.beginPath();
        ctx.roundRect(20, yPos, width - 40, sectionHeight, 10);
        ctx.fill();
        
        ctx.fillStyle = '#facc15';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(`\uD83C\uDF96\uFE0F Insignias (${badgesConquistados.length})`, 35, yPos + 22);
        
        const badgesToShow = badgesConquistados.slice(0, maxBadgesPerRow * 2);
        
        badgesToShow.forEach((badge, i) => {
          const row = Math.floor(i / maxBadgesPerRow);
          const col = i % maxBadgesPerRow;
          const badgesInRow = row === 0 
            ? Math.min(badgesToShow.length, maxBadgesPerRow) 
            : badgesToShow.length - maxBadgesPerRow;
          const rowWidth = badgesInRow * (badgeSize + badgeGap) - badgeGap;
          const rowStartX = (width - rowWidth) / 2;
          
          const x = rowStartX + col * (badgeSize + badgeGap);
          const y = yPos + 35 + row * (badgeSize + 10);
          const cx = x + badgeSize / 2;
          const cy = y + badgeSize / 2;
          
          ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
          ctx.beginPath();
          ctx.arc(cx + 1, cy + 2, badgeSize / 2.3, 0, Math.PI * 2);
          ctx.fill();
          
          const corPrimaria = badge.cor_primaria || '#10b981';
          const corSecundaria = badge.cor_secundaria || '#059669';
          const badgeGradient = ctx.createRadialGradient(cx - 4, cy - 4, 0, cx, cy, badgeSize / 2);
          badgeGradient.addColorStop(0, corPrimaria);
          badgeGradient.addColorStop(1, corSecundaria);
          ctx.fillStyle = badgeGradient;
          ctx.beginPath();
          ctx.arc(cx, cy, badgeSize / 2 - 2, 0, Math.PI * 2);
          ctx.fill();
          
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
          ctx.lineWidth = 1.5;
          ctx.stroke();
          
          drawBadgeIcon(ctx, badge.icone, cx, cy, badgeSize);
        });
        
        yPos += sectionHeight + 10;
      }
      
      // ========== FOOTER ==========
      const footerY = Math.max(yPos + 10, height - 40);
      
      const lineGradient = ctx.createLinearGradient(20, footerY, width - 20, footerY);
      lineGradient.addColorStop(0, '#10b981');
      lineGradient.addColorStop(0.5, '#06b6d4');
      lineGradient.addColorStop(1, '#10b981');
      ctx.strokeStyle = lineGradient;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(20, footerY);
      ctx.lineTo(width - 20, footerY);
      ctx.stroke();
      
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Arial';
      ctx.fillText(`Gerado em ${new Date().toLocaleDateString('pt-BR')}`, 20, footerY + 20);
      ctx.textAlign = 'right';
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 11px Arial';
      ctx.fillText('Ranking Run', width - 20, footerY + 20);
      ctx.textAlign = 'left';

      const imageUrl = canvas.toDataURL('image/png');
      return imageUrl;
    } catch (error) {
      console.error('Erro ao gerar card:', error);
      throw error;
    }
};
