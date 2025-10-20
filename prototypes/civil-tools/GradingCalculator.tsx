import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { useState } from 'react';
import { Calculator, AlertCircle, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react';

export default function GradingCalculator() {
  const [existingElev, setExistingElev] = useState('100.0');
  const [proposedElev, setProposedElev] = useState('102.5');
  const [distance, setDistance] = useState([100]);
  const [area, setArea] = useState('5000');
  
  const existing = parseFloat(existingElev) || 0;
  const proposed = parseFloat(proposedElev) || 0;
  const areaValue = parseFloat(area) || 0;
  const cut = existing > proposed ? existing - proposed : 0;
  const fill = proposed > existing ? proposed - existing : 0;
  const slope = ((proposed - existing) / distance[0]) * 100;
  const cutVolume = (areaValue * cut) / 27;
  const fillVolume = (areaValue * fill) / 27;

  const getSlopeStatus = () => {
    const absSlope = Math.abs(slope);
    if (absSlope <= 2) return { color: 'green', text: 'Gentle slope - accessible', icon: CheckCircle };
    if (absSlope <= 10) return { color: 'green', text: 'Moderate slope - typical', icon: CheckCircle };
    if (absSlope <= 33) return { color: 'yellow', text: 'Steep - within limits', icon: AlertCircle };
    return { color: 'red', text: 'Very steep - stabilization required', icon: AlertCircle };
  };

  const status = getSlopeStatus();

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Calculator className="h-8 w-8 text-blue-600" />
              <h1 className="text-3xl font-bold">Grading Calculator</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Interactive grading and earthwork calculations
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Input */}
          <Card>
            <CardHeader>
              <CardTitle>Grading Parameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Existing Elevation (ft)</Label>
                <Input
                  type="number"
                  value={existingElev}
                  onChange={(e) => setExistingElev(e.target.value)}
                  step="0.1"
                  data-testid="input-existing-elevation"
                />
              </div>

              <div className="space-y-2">
                <Label>Proposed Elevation (ft)</Label>
                <Input
                  type="number"
                  value={proposedElev}
                  onChange={(e) => setProposedElev(e.target.value)}
                  step="0.1"
                  data-testid="input-proposed-elevation"
                />
              </div>

              <div className="space-y-2">
                <Label>Horizontal Distance: {distance[0]} ft</Label>
                <Slider
                  value={distance}
                  onValueChange={setDistance}
                  min={10}
                  max={200}
                  step={5}
                  data-testid="slider-distance"
                />
              </div>

              {/* Live Preview */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Quick Direction</span>
                  <div className="flex items-center gap-2">
                    {proposed > existing ? (
                      <>
                        <TrendingUp className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-medium text-green-600">Filling {fill.toFixed(2)} ft</span>
                      </>
                    ) : proposed < existing ? (
                      <>
                        <TrendingDown className="h-5 w-5 text-red-600" />
                        <span className="text-sm font-medium text-red-600">Cutting {cut.toFixed(2)} ft</span>
                      </>
                    ) : (
                      <span className="text-sm text-muted-foreground">No change</span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <Card>
            <CardHeader>
              <CardTitle>Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Cut</p>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {cut.toFixed(2)} ft
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Fill</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {fill.toFixed(2)} ft
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Slope</span>
                  <span className="text-lg font-mono font-medium">
                    {slope.toFixed(2)}% ({Math.abs(slope) > 0 ? (1 / (Math.abs(slope) / 100)).toFixed(1) : '∞'}:1)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Elevation Change</span>
                  <span className="text-lg font-mono font-medium">
                    {(proposed - existing).toFixed(2)} ft
                  </span>
                </div>
              </div>

              {/* Validation */}
              <div className="space-y-2 pt-4 border-t">
                <p className="text-sm font-medium">Validation</p>
                <div className="space-y-2">
                  <div className={`flex items-center gap-2 text-sm ${
                    status.color === 'green' ? 'text-green-600 dark:text-green-400' :
                    status.color === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-red-600 dark:text-red-400'
                  }`}>
                    <status.icon className="h-4 w-4" />
                    <span>{status.text}</span>
                  </div>
                  
                  {Math.abs(proposed - existing) < 8 ? (
                    <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                      <CheckCircle className="h-4 w-4" />
                      <span>Elevation change acceptable</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                      <AlertCircle className="h-4 w-4" />
                      <span>Large elevation change - review required</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Earthwork Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Earthwork Volume Estimator</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4">
              <div>
                <Label className="text-xs">Area (sq ft)</Label>
                <Input 
                  value={area} 
                  onChange={(e) => setArea(e.target.value)}
                  type="number" 
                  className="mt-1" 
                  data-testid="input-area" 
                />
              </div>
              <div>
                <Label className="text-xs">Avg Cut Depth (ft)</Label>
                <Input value={cut.toFixed(2)} readOnly className="mt-1 bg-muted" />
              </div>
              <div>
                <Label className="text-xs">Cut Volume</Label>
                <p className="text-lg font-mono font-medium mt-1 text-red-600 dark:text-red-400">
                  {cutVolume.toFixed(0)} CY
                </p>
              </div>
              <div>
                <Label className="text-xs">Fill Volume</Label>
                <p className="text-lg font-mono font-medium mt-1 text-green-600 dark:text-green-400">
                  {fillVolume.toFixed(0)} CY
                </p>
              </div>
            </div>

            {/* Balance Summary */}
            <div className="mt-6 p-4 bg-muted/30 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Net Balance</span>
                <div className="flex items-center gap-3">
                  {cutVolume > fillVolume ? (
                    <>
                      <span className="font-mono font-medium text-red-600 dark:text-red-400">
                        {(cutVolume - fillVolume).toFixed(0)} CY excess cut
                      </span>
                      <Badge variant="outline" className="text-red-600">Export Required</Badge>
                    </>
                  ) : fillVolume > cutVolume ? (
                    <>
                      <span className="font-mono font-medium text-green-600 dark:text-green-400">
                        {(fillVolume - cutVolume).toFixed(0)} CY import needed
                      </span>
                      <Badge variant="outline" className="text-green-600">Import Required</Badge>
                    </>
                  ) : (
                    <>
                      <span className="font-mono font-medium">Balanced</span>
                      <Badge variant="outline" className="text-green-600">Zero Balance</Badge>
                    </>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
