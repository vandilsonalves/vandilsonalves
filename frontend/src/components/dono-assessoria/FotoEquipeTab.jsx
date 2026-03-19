// /app/frontend/src/components/dono-assessoria/FotoEquipeTab.jsx
import { useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Image, Upload, Camera, Trash2, MapPin, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const FotoEquipeTab = ({
  assessoria,
  uploadingFoto,
  fotoInputRef,
  onUploadFoto,
  onRemoverFoto,
  getSeloIcon,
  getSeloColor
}) => (
  <div className="space-y-6" data-testid="foto-tab">
    <h2 className="text-2xl font-bold text-white">Foto da Assessoria</h2>
    <p className="text-slate-400">
      A foto da sua assessoria aparecerá na página pública e no selo oficial.
    </p>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Preview da Foto Atual */}
      <FotoAtualCard 
        assessoria={assessoria}
        uploadingFoto={uploadingFoto}
        onRemoverFoto={onRemoverFoto}
      />

      {/* Upload de Nova Foto */}
      <UploadFotoCard
        assessoria={assessoria}
        uploadingFoto={uploadingFoto}
        fotoInputRef={fotoInputRef}
        onUploadFoto={onUploadFoto}
      />
    </div>

    {/* Preview de como aparece na página */}
    <PreviewCard
      assessoria={assessoria}
      getSeloIcon={getSeloIcon}
      getSeloColor={getSeloColor}
    />
  </div>
);

const FotoAtualCard = ({ assessoria, uploadingFoto, onRemoverFoto }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardHeader>
      <CardTitle className="text-white flex items-center gap-2">
        <Image className="w-5 h-5 text-amber-500" />
        Foto Atual
      </CardTitle>
    </CardHeader>
    <CardContent className="p-6">
      <div className="flex flex-col items-center">
        {assessoria.foto_url ? (
          <div className="relative group">
            <img 
              src={assessoria.foto_url.startsWith('http') ? assessoria.foto_url : `${BACKEND_URL}${assessoria.foto_url}`}
              alt={assessoria.nome}
              className="w-48 h-48 object-cover rounded-2xl shadow-lg border-4 border-amber-500/30"
            />
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl flex items-center justify-center">
              <Button
                variant="destructive"
                size="sm"
                onClick={onRemoverFoto}
                disabled={uploadingFoto}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Remover
              </Button>
            </div>
          </div>
        ) : (
          <div className="w-48 h-48 bg-slate-700 rounded-2xl flex flex-col items-center justify-center border-2 border-dashed border-slate-600">
            <Camera className="w-12 h-12 text-slate-500 mb-2" />
            <p className="text-sm text-slate-500">Sem foto</p>
          </div>
        )}

        <p className="mt-4 text-sm text-slate-400 text-center">
          {assessoria.foto_url 
            ? 'Passe o mouse sobre a foto para ver a opção de remover'
            : 'Sua assessoria ainda não tem foto'
          }
        </p>
      </div>
    </CardContent>
  </Card>
);

const UploadFotoCard = ({ assessoria, uploadingFoto, fotoInputRef, onUploadFoto }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardHeader>
      <CardTitle className="text-white flex items-center gap-2">
        <Upload className="w-5 h-5 text-emerald-500" />
        {assessoria.foto_url ? 'Trocar Foto' : 'Enviar Foto'}
      </CardTitle>
    </CardHeader>
    <CardContent className="p-6">
      <input
        type="file"
        ref={fotoInputRef}
        onChange={onUploadFoto}
        accept="image/jpeg,image/png,image/webp,image/gif"
        className="hidden"
        id="foto-upload"
      />

      <div 
        className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center hover:border-amber-500 transition-colors cursor-pointer"
        onClick={() => fotoInputRef.current?.click()}
      >
        {uploadingFoto ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-amber-500 animate-spin mb-4" />
            <p className="text-white font-medium">Enviando foto...</p>
          </div>
        ) : (
          <>
            <Camera className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-white font-medium mb-2">
              Clique para selecionar uma foto
            </p>
            <p className="text-sm text-slate-400">
              JPEG, PNG, WebP ou GIF - Máximo 5MB
            </p>
          </>
        )}
      </div>

      <div className="mt-4 space-y-2">
        <p className="text-xs text-slate-500">
          <strong>Dica:</strong> Use uma imagem quadrada (1:1) para melhor visualização.
        </p>
        <p className="text-xs text-slate-500">
          A foto aparecerá na página pública da assessoria e no selo oficial.
        </p>
      </div>

      <Button
        className="w-full mt-4 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
        onClick={() => fotoInputRef.current?.click()}
        disabled={uploadingFoto}
      >
        {uploadingFoto ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Enviando...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4 mr-2" />
            {assessoria.foto_url ? 'Trocar Foto' : 'Selecionar Foto'}
          </>
        )}
      </Button>
    </CardContent>
  </Card>
);

const PreviewCard = ({ assessoria, getSeloIcon, getSeloColor }) => (
  <Card className="bg-slate-800 border-slate-700">
    <CardHeader>
      <CardTitle className="text-white">Preview - Como sua assessoria aparece</CardTitle>
    </CardHeader>
    <CardContent className="p-6">
      <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-6">
          {assessoria.foto_url ? (
            <div className="relative">
              <img 
                src={assessoria.foto_url.startsWith('http') ? assessoria.foto_url : `${BACKEND_URL}${assessoria.foto_url}`}
                alt={assessoria.nome}
                className="w-24 h-24 object-cover rounded-2xl shadow-lg border-4 border-white/30"
              />
              <div className={`absolute -bottom-2 -right-2 w-10 h-10 ${getSeloColor(assessoria.selo)} rounded-full flex items-center justify-center text-2xl shadow-md border-2 border-white`}>
                {getSeloIcon(assessoria.selo)}
              </div>
            </div>
          ) : (
            <div className={`w-24 h-24 rounded-2xl ${getSeloColor(assessoria.selo)} flex items-center justify-center text-5xl shadow-lg border-4 border-white/30`}>
              {getSeloIcon(assessoria.selo)}
            </div>
          )}
          <div>
            <h3 className="text-2xl font-bold">{assessoria.nome}</h3>
            <p className="text-amber-100 flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              {assessoria.cidade}, {assessoria.estado}
            </p>
            <Badge className="mt-2 bg-white/20 text-white">
              SELO {assessoria.selo?.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);
