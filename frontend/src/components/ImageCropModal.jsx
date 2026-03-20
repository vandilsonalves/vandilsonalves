// /app/frontend/src/components/ImageCropModal.jsx
// Modal para recortar/enquadrar imagem de perfil

import { useState, useRef, useCallback } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, Check, X, ZoomIn, ZoomOut, RotateCw } from 'lucide-react';
import { Slider } from '@/components/ui/slider';

const ImageCropModal = ({ 
  isOpen, 
  onClose, 
  imageSrc, 
  onCropComplete,
  aspectRatio = 1 // 1:1 para foto de perfil quadrada
}) => {
  const imgRef = useRef(null);
  const [crop, setCrop] = useState({
    unit: '%',
    width: 80,
    height: 80,
    x: 10,
    y: 10
  });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [scale, setScale] = useState(1);
  const [rotate, setRotate] = useState(0);
  const [loading, setLoading] = useState(false);

  const onImageLoad = useCallback((e) => {
    const { width, height } = e.currentTarget;
    
    // Centralizar o crop inicial
    const cropSize = Math.min(width, height) * 0.8;
    const cropX = (width - cropSize) / 2;
    const cropY = (height - cropSize) / 2;
    
    setCrop({
      unit: 'px',
      width: cropSize,
      height: cropSize,
      x: cropX,
      y: cropY
    });
  }, []);

  const getCroppedImg = useCallback(async () => {
    if (!completedCrop || !imgRef.current) return null;

    const image = imgRef.current;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) return null;

    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;

    // Tamanho final da imagem (400x400 para perfil)
    const outputSize = 400;
    canvas.width = outputSize;
    canvas.height = outputSize;

    // Aplicar transformações
    ctx.imageSmoothingQuality = 'high';
    
    // Centralizar e aplicar rotação
    ctx.translate(outputSize / 2, outputSize / 2);
    ctx.rotate((rotate * Math.PI) / 180);
    ctx.scale(scale, scale);
    ctx.translate(-outputSize / 2, -outputSize / 2);

    // Desenhar a imagem recortada
    ctx.drawImage(
      image,
      completedCrop.x * scaleX,
      completedCrop.y * scaleY,
      completedCrop.width * scaleX,
      completedCrop.height * scaleY,
      0,
      0,
      outputSize,
      outputSize
    );

    // Converter para blob
    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          resolve(blob);
        },
        'image/jpeg',
        0.9
      );
    });
  }, [completedCrop, rotate, scale]);

  const handleSave = async () => {
    setLoading(true);
    try {
      const croppedBlob = await getCroppedImg();
      if (croppedBlob) {
        // Converter blob para File
        const file = new File([croppedBlob], 'profile-photo.jpg', { type: 'image/jpeg' });
        onCropComplete(file);
      }
    } catch (error) {
      console.error('Erro ao recortar imagem:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRotate = () => {
    setRotate((prev) => (prev + 90) % 360);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-slate-700 max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            Enquadrar Foto de Perfil
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Área de Crop */}
          <div className="flex justify-center bg-slate-800 rounded-lg p-4 max-h-[400px] overflow-hidden">
            <ReactCrop
              crop={crop}
              onChange={(c) => setCrop(c)}
              onComplete={(c) => setCompletedCrop(c)}
              aspect={aspectRatio}
              circularCrop
              className="max-h-[350px]"
            >
              <img
                ref={imgRef}
                src={imageSrc}
                alt="Imagem para recortar"
                onLoad={onImageLoad}
                style={{
                  transform: `scale(${scale}) rotate(${rotate}deg)`,
                  maxHeight: '350px',
                  objectFit: 'contain'
                }}
              />
            </ReactCrop>
          </div>

          {/* Controles */}
          <div className="space-y-4 bg-slate-800 rounded-lg p-4">
            {/* Zoom */}
            <div className="flex items-center gap-4">
              <ZoomOut className="w-4 h-4 text-slate-400" />
              <Slider
                value={[scale]}
                onValueChange={(v) => setScale(v[0])}
                min={0.5}
                max={2}
                step={0.1}
                className="flex-1"
              />
              <ZoomIn className="w-4 h-4 text-slate-400" />
              <span className="text-sm text-slate-400 w-12 text-right">{Math.round(scale * 100)}%</span>
            </div>

            {/* Rotação */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Rotação: {rotate}°</span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRotate}
                className="border-slate-600"
              >
                <RotateCw className="w-4 h-4 mr-2" />
                Girar 90°
              </Button>
            </div>
          </div>

          {/* Dica */}
          <p className="text-xs text-slate-500 text-center">
            Arraste o círculo para enquadrar sua foto. Use o zoom para ajustar o tamanho.
          </p>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose} className="border-slate-600">
            <X className="w-4 h-4 mr-2" />
            Cancelar
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={loading || !completedCrop}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Check className="w-4 h-4 mr-2" />
            )}
            Salvar Foto
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ImageCropModal;
