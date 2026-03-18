import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { 
  Users, Search, Plus, Eye, Edit, Trash2, Download, 
  ArrowRightLeft, Award, Loader2, MessageSquare, Crown
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ESTADOS_BR = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const DashboardAtletas = ({ 
  atletas = [], 
  loadingAtletas, 
  filtroCategoria, 
  setFiltroCategoria,
  filtroModalidade,
  setFiltroModalidade,
  filtroEquipe,
  setFiltroEquipe,
  searchQuery,
  setSearchQuery,
  token,
  onRefresh,
  onEditAtleta,
  onDeleteAtleta,
  onTransferirModalidade,
  onPromoverDono,
  onExportAtletas,
  onViewAtleta,
  onEnviarMensagem
}) => {
  // Garantir que atletas é sempre um array
  const atletasArray = Array.isArray(atletas) ? atletas : [];
  
  // Filtrar atletas localmente
  const atletasFiltrados = atletasArray
    .filter(a => {
      const matchSearch = !searchQuery || 
        a.nome?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.equipe?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.cidade?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchModalidade = filtroModalidade === 'all' || 
        (filtroModalidade === 'profissional_amador' && a.modalidade_usuario !== 'povao_pace_livre') ||
        (filtroModalidade === 'povao_pace_livre' && a.modalidade_usuario === 'povao_pace_livre');
      
      // Filtro de categoria/gênero
      let matchCategoria = filtroCategoria === 'all';
      if (!matchCategoria) {
        if (filtroCategoria === 'masculino') {
          matchCategoria = a.genero === 'M' && a.categoria !== 'pcd' && a.categoria !== 'cadeirante';
        } else if (filtroCategoria === 'feminino') {
          matchCategoria = a.genero === 'F' && a.categoria !== 'pcd' && a.categoria !== 'cadeirante';
        } else if (filtroCategoria === 'pcd_m') {
          matchCategoria = a.genero === 'M' && a.categoria === 'pcd';
        } else if (filtroCategoria === 'pcd_f') {
          matchCategoria = a.genero === 'F' && a.categoria === 'pcd';
        } else if (filtroCategoria === 'cadeirante_m') {
          matchCategoria = a.genero === 'M' && a.categoria === 'cadeirante';
        } else if (filtroCategoria === 'cadeirante_f') {
          matchCategoria = a.genero === 'F' && a.categoria === 'cadeirante';
        }
      }
      
      // Filtro de equipe/assessoria
      let matchEquipe = !filtroEquipe || filtroEquipe === 'all';
      if (!matchEquipe) {
        const temEquipe = a.equipe && a.equipe.trim() !== '' && 
                          a.equipe.toLowerCase() !== 'individual' && 
                          a.equipe.toLowerCase() !== 'sem equipe';
        if (filtroEquipe === 'com_assessoria') {
          matchEquipe = temEquipe;
        } else if (filtroEquipe === 'individual') {
          matchEquipe = !temEquipe;
        } else if (filtroEquipe === 'dono_assessoria') {
          matchEquipe = a.role === 'dono_assessoria' || a.is_dono_assessoria === true;
        }
      }
      
      return matchSearch && matchModalidade && matchCategoria && matchEquipe;
    })
    .sort((a, b) => (a.nome || '').localeCompare(b.nome || ''));

  const getCategoriaLabel = (a) => {
    if (a.categoria === 'pcd') return `PCD ${a.genero === 'M' ? 'Masc' : 'Fem'}`;
    if (a.categoria === 'cadeirante') return `Cadeirante ${a.genero === 'M' ? 'Masc' : 'Fem'}`;
    return a.genero === 'M' ? 'Masculino' : 'Feminino';
  };

  const getModalidadeBadge = (a) => {
    if (a.modalidade_usuario === 'povao_pace_livre') {
      return <Badge className="bg-purple-500 text-white text-xs">Povão</Badge>;
    }
    return <Badge className="bg-green-500 text-white text-xs">Pro/Amador</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header com Filtros */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-green-500" />
              Gerenciar Atletas
              <Badge variant="secondary">{atletasFiltrados.length} atletas</Badge>
            </CardTitle>
            <div className="flex flex-wrap gap-2">
              <Button onClick={onExportAtletas} variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportar Dados
              </Button>
              <Button onClick={() => onEditAtleta(null)} size="sm" className="bg-green-500 hover:bg-green-600">
                <Plus className="w-4 h-4 mr-2" />
                Adicionar
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4">
            {/* Busca */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Buscar por nome, equipe ou cidade..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Filtro por Categoria */}
            <Select value={filtroCategoria} onValueChange={setFiltroCategoria}>
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="masculino">Masculino</SelectItem>
                <SelectItem value="feminino">Feminino</SelectItem>
                <SelectItem value="pcd_m">PCD Masc.</SelectItem>
                <SelectItem value="pcd_f">PCD Fem.</SelectItem>
                <SelectItem value="cadeirante_m">Cadeirante M</SelectItem>
                <SelectItem value="cadeirante_f">Cadeirante F</SelectItem>
              </SelectContent>
            </Select>

            {/* Filtro por Modalidade */}
            <Select value={filtroModalidade} onValueChange={setFiltroModalidade}>
              <SelectTrigger className="w-full md:w-44">
                <SelectValue placeholder="Modalidade" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas Modalidades</SelectItem>
                <SelectItem value="profissional_amador">Pro/Amador</SelectItem>
                <SelectItem value="povao_pace_livre">Povão</SelectItem>
              </SelectContent>
            </Select>

            {/* Filtro por Equipe/Assessoria */}
            <Select value={filtroEquipe || 'all'} onValueChange={setFiltroEquipe}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Equipe" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas Equipes</SelectItem>
                <SelectItem value="com_assessoria">Com Assessoria</SelectItem>
                <SelectItem value="individual">Individual</SelectItem>
                <SelectItem value="dono_assessoria">Dono de Assessoria</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Atletas */}
      <Card>
        <CardContent className="p-0">
          {loadingAtletas ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-green-500" />
            </div>
          ) : atletasFiltrados.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Users className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Nenhum atleta encontrado</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
              {atletasFiltrados.map((atleta) => (
                <div
                  key={atleta.id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-white dark:bg-slate-800"
                >
                  <div className="flex items-start gap-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src={atleta.foto_url ? `${BACKEND_URL}${atleta.foto_url}` : undefined} />
                      <AvatarFallback className="bg-green-100 text-green-600">
                        {atleta.nome?.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm truncate">{atleta.nome}</h4>
                      <p className="text-xs text-slate-500 truncate">{atleta.email}</p>
                      <div className="flex items-center gap-1 mt-1 flex-wrap">
                        <Badge variant="outline" className="text-xs">
                          {getCategoriaLabel(atleta)}
                        </Badge>
                        {getModalidadeBadge(atleta)}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        {atleta.equipe || 'Sem equipe'} • {atleta.cidade}/{atleta.estado}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-end gap-1 mt-3 pt-3 border-t">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewAtleta(atleta)}
                      title="Ver Perfil"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    
                    {/* Botão Enviar Mensagem */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEnviarMensagem && onEnviarMensagem(atleta)}
                      title="Enviar Mensagem"
                      className="text-blue-500 hover:text-blue-700"
                    >
                      <MessageSquare className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEditAtleta(atleta)}
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    
                    {/* Botão Transferir - apenas para atletas normais (não PCD/Cadeirante) */}
                    {atleta.categoria === 'normal' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onTransferirModalidade(atleta)}
                        title="Transferir Modalidade"
                        className="text-purple-500 hover:text-purple-700"
                      >
                        <ArrowRightLeft className="w-4 h-4" />
                      </Button>
                    )}

                    {/* Botão Promover Dono - apenas para atletas com equipe e que não são donos */}
                    {atleta.equipe && atleta.role !== 'dono_assessoria' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onPromoverDono(atleta)}
                        title="Promover a Dono de Assessoria"
                        className="text-amber-500 hover:text-amber-700"
                      >
                        <Crown className="w-4 h-4" />
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDeleteAtleta(atleta.id)}
                      title="Excluir"
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardAtletas;
