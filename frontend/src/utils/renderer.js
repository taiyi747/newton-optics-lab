import { RENDER_CONFIG } from './config.js';
import { translations } from './i18n.js';

const canvasState = new Map();

let currentLang = 'zh';

export function setRendererLang(lang) {
    currentLang = lang;
}

function getTranslation(key) {
    return translations[currentLang]?.[key] || key;
}

class NewtonRingRenderer {
    getCanvas(id, useDpr = true) {
        const canvas = document.getElementById(id);
        if (!canvas) {
            return null;
        }

        const parent = canvas.parentElement;
        if (parent) {
            const rect = parent.getBoundingClientRect();
            const width = Math.max(1, Math.floor(rect.width));
            const height = Math.max(1, Math.floor(rect.height));
            const dpr = useDpr ? (window.devicePixelRatio || 1) : 1;
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            canvas.style.width = `${width}px`;
            canvas.style.height = `${height}px`;
            canvasState.set(id, { dpr, logicalWidth: width, logicalHeight: height });
        }

        return canvas;
    }

    getCanvasState(id) {
        return canvasState.get(id) || {};
    }

    setCanvasData(id, data) {
        const existing = canvasState.get(id) || {};
        canvasState.set(id, { ...existing, ...data });
    }

    wavelengthToRGB(wavelength) {
        let r = 0;
        let g = 0;
        let b = 0;

        if (wavelength >= 380 && wavelength < 440) {
            r = -(wavelength - 440) / (440 - 380);
            b = 1;
        } else if (wavelength < 490) {
            g = (wavelength - 440) / (490 - 440);
            b = 1;
        } else if (wavelength < 510) {
            g = 1;
            b = -(wavelength - 510) / (510 - 490);
        } else if (wavelength < 580) {
            r = (wavelength - 510) / (580 - 510);
            g = 1;
        } else if (wavelength < 645) {
            r = 1;
            g = -(wavelength - 645) / (645 - 580);
        } else if (wavelength <= 780) {
            r = 1;
        }

        let factor = 0;
        if (wavelength >= 380 && wavelength < 420) {
            factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380);
        } else if (wavelength < 701) {
            factor = 1;
        } else if (wavelength <= 780) {
            factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 701);
        }

        return {
            r: Math.round(r * factor * 255),
            g: Math.round(g * factor * 255),
            b: Math.round(b * factor * 255),
        };
    }

    computeAirGap(r, { radius, r2, isNonContact, isDoubleLens, spacing = 0, hMax }) {
        let h;
        if (isDoubleLens && r2 > 0) {
            h = (r * r / 2) * (1 / radius + 1 / r2);
        } else {
            h = r * r / (2 * radius);
            if (hMax !== undefined) {
                h = Math.min(h, hMax);
            }
        }

        if (isNonContact) {
            h += spacing * 1e-9;
        }
        return h;
    }

    calculateIntensityData(radius, wavelength, refractive, isNonContact = false, spacing = 0, isDoubleLens = false, r2 = 0) {
        const lam = wavelength * 1e-9;
        const maxR = Math.sqrt(RENDER_CONFIG.MAX_RING_COUNT * lam * radius);
        const rValues = [];
        const intensityValues = [];

        for (let i = 0; i < RENDER_CONFIG.INTENSITY_SAMPLE_POINTS; i += 1) {
            const r = -maxR + (2 * maxR * i) / (RENDER_CONFIG.INTENSITY_SAMPLE_POINTS - 1);
            rValues.push(r);

            let h;
            if (isDoubleLens && r2 > 0) {
                h = isNonContact
                    ? (r * r / 2) * (1 / radius - 1 / r2)
                    : (r * r / 2) * (1 / radius + 1 / r2);
            } else {
                h = r * r / (2 * radius);
            }

            if (isNonContact) {
                h += spacing * 1e-9;
            }

            const phase = 4 * Math.PI * refractive * h / lam;
            intensityValues.push(2 * (1 - Math.cos(phase)));
        }

        return { rValues, intensityValues, maxR };
    }

    drawRingPattern(canvasId, wavelength, config) {
        const canvas = this.getCanvas(canvasId, false);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            this._showCanvasError(canvasId, 'Canvas 不可用');
            return;
        }

        const width = canvas.width;
        const height = canvas.height;
        if (width <= 0 || height <= 0) return;

        const pixelData = ctx.createImageData(width, height);
        const data = pixelData.data;
        const rgb = this.wavelengthToRGB(wavelength);
        const wl = wavelength * 1e-9;
        if (!isFinite(wl) || wl <= 0) {
            this._showCanvasError(canvasId, '参数异常：波长无效');
            return;
        }

        const centerX = width / 2;
        const centerY = height / 2;
        const maxRadius = Math.min(width, height) / 2 * RENDER_CONFIG.CANVAS_MARGIN;
        const radiusScale = config.radiusScale || RENDER_CONFIG.RADIUS_SCALE_NORMAL;

        for (let y = 0; y < height; y += 1) {
            for (let x = 0; x < width; x += 1) {
                const dx = x - centerX;
                const dy = y - centerY;
                const r = Math.sqrt(dx * dx + dy * dy) / maxRadius * radiusScale;
                const h = this.computeAirGap(r, config);
                const phase = Math.PI * (2 * config.refractive * h + wl / 2) / wl;
                const intensity = isFinite(phase) ? Math.cos(phase) ** 2 : 0;
                const index = (y * width + x) * 4;

                data[index] = rgb.r * intensity;
                data[index + 1] = rgb.g * intensity;
                data[index + 2] = rgb.b * intensity;
                data[index + 3] = 255;
            }
        }

        ctx.putImageData(pixelData, 0, 0);
    }

    drawNewtonRing(canvasId, wavelength, radius, spacing, refractive, isNonContact = false) {
        this.drawRingPattern(canvasId, wavelength, {
            radius,
            refractive,
            isNonContact,
            isDoubleLens: false,
            spacing,
            radiusScale: RENDER_CONFIG.RADIUS_SCALE_NORMAL,
        });
    }

    drawTruncatedRing(canvasId, wavelength, radius, truncatedHeight, refractive) {
        this.drawRingPattern(canvasId, wavelength, {
            radius,
            refractive,
            isDoubleLens: false,
            isNonContact: false,
            hMax: truncatedHeight * 1e-9,
            radiusScale: RENDER_CONFIG.RADIUS_SCALE_NORMAL,
        });
    }

    drawDoubleLensRing(canvasId, wavelength, r1, r2, refractive, isNonContact = false, spacing = 0) {
        this.drawRingPattern(canvasId, wavelength, {
            radius: r1,
            r2,
            refractive,
            isNonContact,
            isDoubleLens: true,
            spacing,
            radiusScale: RENDER_CONFIG.RADIUS_SCALE_DOUBLE_LENS,
        });
    }

    _drawAxes(ctx, width, height, padding, plotWidth, plotHeight) {
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        for (let i = 1; i < 5; i += 1) {
            const x = padding + (plotWidth / 5) * i;
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            const y = padding + (plotHeight / 5) * i;
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
        }
        ctx.stroke();

        ctx.strokeStyle = '#374151';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.setLineDash([5, 5]);
        ctx.moveTo(width / 2, padding);
        ctx.lineTo(width / 2, height - padding);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    _drawIntensityPlot(ctx, canvas, plotData, xlim, canvasId) {
        const { width, height, padding, plotWidth, plotHeight, rValues, intensityValues } = plotData;
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, width, height);
        this._drawAxes(ctx, width, height, padding, plotWidth, plotHeight);

        const rToX = (r) => {
            const rMm = r * 1000;
            if (rMm < xlim[0] || rMm > xlim[1]) {
                return null;
            }
            return padding + ((rMm - xlim[0]) / (xlim[1] - xlim[0])) * plotWidth;
        };
        const intensityToY = (intensity) => height - padding - (intensity / 5) * plotHeight * 0.8 - plotHeight * 0.1;

        ctx.strokeStyle = '#165DFF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        let firstPoint = true;
        for (let i = 0; i < rValues.length; i += 1) {
            const x = rToX(rValues[i]);
            if (x === null) {
                continue;
            }
            const y = intensityToY(intensityValues[i]);
            if (firstPoint) {
                ctx.moveTo(x, y);
                firstPoint = false;
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        const centerIndex = Math.floor(rValues.length / 2);
        const centerX = rToX(0);
        if (centerX !== null) {
            ctx.fillStyle = '#ef4444';
            ctx.beginPath();
            ctx.arc(centerX, intensityToY(intensityValues[centerIndex]), 4, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.fillStyle = '#374151';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('半径 r (mm)', width / 2, height - 15);
        ctx.save();
        ctx.translate(20, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('光强 I (相对单位)', 0, 0);
        ctx.restore();

        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#6b7280';
        for (let i = 0; i <= 4; i += 1) {
            const value = xlim[0] + (xlim[1] - xlim[0]) * (i / 4);
            const x = padding + (plotWidth / 4) * i;
            ctx.fillText(value.toFixed(0), x, height - padding + 15);
        }
        for (let i = 0; i <= 5; i += 1) {
            const y = height - padding - (plotHeight / 5) * i;
            ctx.textAlign = 'right';
            ctx.fillText(String(i), padding - 10, y + 4);
        }

        const title = plotData.isDoubleLens && plotData.r2 > 0
            ? `牛顿环光强分布 λ=${plotData.wavelength.toFixed(1)}nm, R1=${plotData.radius.toFixed(2)}m, R2=${plotData.r2.toFixed(2)}m, n=${plotData.refractive.toFixed(3)}`
            : `牛顿环光强分布 λ=${plotData.wavelength.toFixed(1)}nm, R=${plotData.radius.toFixed(2)}m, n=${plotData.refractive.toFixed(3)}`;
        ctx.textAlign = 'center';
        ctx.font = 'bold 14px sans-serif';
        ctx.fillStyle = '#374151';
        ctx.fillText(title, width / 2, 25);

        this.setCanvasData(canvasId, { currentXlim: xlim });
    }

    _showCanvasError(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        const w = canvas.width || 300;
        const h = canvas.height || 200;
        ctx.fillStyle = '#f3f4f6';
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#ef4444';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message, w / 2, h / 2);
    }

    drawIntensityPlot(canvasId, wavelength, radius, refractive, isNonContact = false, spacing = 0, isDoubleLens = false, r2 = 0) {
        const canvas = this.getCanvas(canvasId, true);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            this._showCanvasError(canvasId, 'Canvas 不可用');
            return;
        }
        const { dpr = 1 } = this.getCanvasState(canvasId);
        const width = canvas.width / dpr;
        const height = canvas.height / dpr;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);

        const padding = 50;
        const plotWidth = width - padding * 2;
        const plotHeight = height - padding * 2;
        const { rValues, intensityValues, maxR } = this.calculateIntensityData(
            radius,
            wavelength,
            refractive,
            isNonContact,
            spacing,
            isDoubleLens,
            r2,
        );

        const intensityData = {
            wavelength,
            radius,
            refractive,
            isNonContact,
            spacing,
            isDoubleLens,
            r2,
            maxR,
            width,
            height,
            padding,
            plotWidth,
            plotHeight,
            rValues,
            intensityValues,
            currentXlim: [-4, 4],
        };

        this.setCanvasData(canvasId, intensityData);
        this._drawIntensityPlot(ctx, canvas, intensityData, [-4, 4], canvasId);
    }

    redrawIntensityPlotWithXlim(canvasId, xlim) {
        const state = this.getCanvasState(canvasId);
        if (!state.currentXlim) {
            return;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        const { dpr = 1 } = state;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.scale(dpr, dpr);
        this._drawIntensityPlot(ctx, canvas, state, xlim, canvasId);
    }

    drawPixelRing(canvasId, wavelength, { radius, radiusScale, useDpr = true, noise = 0 }) {
        const canvas = this.getCanvas(canvasId, useDpr);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            this._showCanvasError(canvasId, 'Canvas 不可用');
            return;
        }
        const { dpr = 1 } = this.getCanvasState(canvasId);
        const width = canvas.width / dpr;
        const height = canvas.height / dpr;
        const rgb = this.wavelengthToRGB(wavelength);
        const wl = wavelength * 1e-9;
        const pixelData = ctx.createImageData(width, height);
        const data = pixelData.data;
        const centerX = width / 2;
        const centerY = height / 2;
        const maxRadius = Math.min(width, height) / 2 * RENDER_CONFIG.CANVAS_MARGIN;

        if (useDpr) {
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.scale(dpr, dpr);
        }
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, width, height);

        for (let y = 0; y < height; y += 1) {
            for (let x = 0; x < width; x += 1) {
                const dx = x - centerX;
                const dy = y - centerY;
                const r = Math.sqrt(dx * dx + dy * dy) / maxRadius * radiusScale;
                const h = r * r / (2 * radius);
                const phase = Math.PI * (2 * h + wl / 2) / wl;
                const rawIntensity = Math.cos(phase) ** 2;
                const intensity = noise > 0
                    ? Math.max(0, Math.min(1, rawIntensity + (Math.random() - 0.5) * noise))
                    : rawIntensity;
                const index = (y * width + x) * 4;
                data[index] = rgb.r * intensity;
                data[index + 1] = rgb.g * intensity;
                data[index + 2] = rgb.b * intensity;
                data[index + 3] = 255;
            }
        }

        ctx.putImageData(pixelData, 0, 0);
    }

    drawDataRawImage(canvasId) {
        this.drawPixelRing(canvasId, 550, { radius: 5, radiusScale: 0.01, useDpr: true, noise: 0.1 });
    }

    drawDataRawImageWithWavelength(canvasId, wavelength) {
        this.drawPixelRing(canvasId, wavelength, { radius: 5, radiusScale: 0.01, useDpr: true, noise: 0.1 });
    }

    drawDataNewtonRing(canvasId, wavelength, R) {
        this.drawPixelRing(canvasId, wavelength, { radius: R, radiusScale: 0.002, useDpr: false, noise: 0 });
    }

    drawDataFitCurve(canvasId, k, dSqExp, a, b, wavelength, n) {
        const canvas = this.getCanvas(canvasId, false);
        if (!canvas) {
            return;
        }

        if (!k?.length || !dSqExp?.length || !isFinite(a) || !isFinite(b)) {
            this._showCanvasError(canvasId, '参数异常：无法绘制拟合曲线');
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            this._showCanvasError(canvasId, 'Canvas 不可用');
            return;
        }
        const width = canvas.width;
        const height = canvas.height;
        const padding = 60;
        const plotWidth = width - 2 * padding;
        const plotHeight = height - 2 * padding;
        const xMin = Math.min(...k) - 1;
        const xMax = Math.max(...k) + 1;
        const yMin = Math.min(...dSqExp) * 0.9;
        const yMax = Math.max(...dSqExp) * 1.1;
        const toX = (value) => padding + ((value - xMin) / (xMax - xMin)) * plotWidth;
        const toY = (value) => height - padding - ((value - yMin) / (yMax - yMin)) * plotHeight;

        ctx.fillStyle = '#f3f4f6';
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        for (let i = 0; i <= 5; i += 1) {
            const x = padding + (plotWidth / 5) * i;
            const y = padding + (plotHeight / 5) * i;
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
        }
        ctx.stroke();

        ctx.strokeStyle = '#374151';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.stroke();

        ctx.strokeStyle = '#165DFF';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(toX(xMin), toY(a * xMin + b));
        ctx.lineTo(toX(xMax), toY(a * xMax + b));
        ctx.stroke();

        for (let i = 0; i < k.length; i += 1) {
            const x = toX(k[i]);
            const yExp = toY(dSqExp[i]);
            const yFit = toY(a * k[i] + b);

            ctx.strokeStyle = '#9ca3af';
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(x, yExp);
            ctx.lineTo(x, yFit);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#ef4444';
            ctx.beginPath();
            ctx.arc(x, yExp, 5, 0, Math.PI * 2);
            ctx.fill();
        }

        const wlM = wavelength * 1e-9;
        const calculatedR = a / (4 * (wlM / n));
        ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
        ctx.fillRect(width - 220, 15, 200, 100);
        ctx.strokeStyle = '#165DFF';
        ctx.strokeRect(width - 220, 15, 200, 100);
        ctx.fillStyle = '#374151';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`斜率 a: ${a.toExponential(4)}`, width - 210, 35);
        ctx.fillText(`截距 b: ${b.toExponential(4)}`, width - 210, 55);
        ctx.fillText(`波长 λ: ${wavelength} nm`, width - 210, 75);
        ctx.fillText(`曲率半径 R: ${calculatedR.toFixed(2)} m`, width - 210, 95);

        ctx.textAlign = 'center';
        ctx.fillText('环序数 k', width / 2, height - 15);
        ctx.save();
        ctx.translate(20, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('直径平方 D² (m²)', 0, 0);
        ctx.restore();
    }

    drawEmptyDataMessage(canvasId, message) {
        const canvas = this.getCanvas(canvasId, false);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        ctx.fillStyle = '#f3f4f6';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#6b7280';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message, width / 2, height / 2);
    }
}

const ringRenderer = new NewtonRingRenderer();
export default ringRenderer;
export { NewtonRingRenderer, canvasState };
