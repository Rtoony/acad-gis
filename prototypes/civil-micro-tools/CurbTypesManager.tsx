import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';
import { Ruler, CheckCircle, AlertCircle } from 'lucide-react';

type CurbType = {
  id: string;
  name: string;
  type: string;
  height: number;
  width: number;
  faceSlope: number;
  material: string;
  adaCompliant: boolean;
  costPerLF: number;
};

export default function CurbTypesManager() {
  const [curbType, setCurbType] = useState('barrier');
  const [height, setHeight] = useState([6]);
  const [faceSlope, setFaceSlope] = useState([90]);
  const [concreteStrength, setConcreteStrength] = useState('3000');
  const [finish, setFinish] = useState('broom');
  
  const isADACompliant = curbType === 'mountable' || (curbType === 'barrier' && height[0] >= 6);

  const curbTypes: CurbType[] = [
    {
      id: 'CT-01',
      name: 'Standard Barrier Curb',
      type: 'barrier',
      height: 6,
      width: 6,
      faceSlope: 90,
      material: 'Concrete 3000 psi',
      adaCompliant: true,
      costPerLF: 18.50,
    },
    {
      id: 'CT-02',
      name: 'Mountable Curb',
      type: 'mountable',
      height: 4,
      width: 12,
      faceSlope: 45,
      material: 'Concrete 3000 psi',
      adaCompliant: true,
      costPerLF: 22.00,
    },
    {
      id: 'CT-03',
      name: 'Integral Curb & Gutter',
      type: 'integral',
      height: 6,
      width: 24,
      faceSlope: 90,
      material: 'Concrete 3500 psi',
      adaCompliant: true,
      costPerLF: 35.00,
    },
  ];

  const applyCurbTemplate = (curb: CurbType) => {
    setCurbType(curb.type);
    setHeight([curb.height]);
    setFaceSlope([curb.faceSlope]);
  };

  const estimatedCost = () => {
    const baseCost = curbType === 'integral' ? 35 : curbType === 'mountable' ? 22 : 18.5;
    const strengthMultiplier = concreteStrength === '4000' ? 1.15 : concreteStrength === '3500' ? 1.08 : 1.0;
    const finishMultiplier = finish === 'exposed' ? 1.25 : finish === 'smooth' ? 1.05 : 1.0;
    return (baseCost * strengthMultiplier * finishMultiplier).toFixed(2);
  };

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Ruler className="h-8 w-8 text-blue-600" />
              <h1 className="text-3xl font-bold">Curb Types Manager</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Parametric curb profiles with ADA compliance validation
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Parametric Editor */}
          <div className="col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Curb Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Curb Type</Label>
                  <Select value={curbType} onValueChange={setCurbType}>
                    <SelectTrigger data-testid="select-curb-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="barrier">Barrier Curb</SelectItem>
                      <SelectItem value="mountable">Mountable Curb</SelectItem>
                      <SelectItem value="rolled">Rolled Curb</SelectItem>
                      <SelectItem value="integral">Integral C&G</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Height: {height[0]}"</Label>
                  <Slider
                    value={height}
                    onValueChange={setHeight}
                    min={4}
                    max={8}
                    step={0.5}
                    data-testid="slider-curb-height"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Face Slope: {faceSlope[0]}°</Label>
                  <Slider
                    value={faceSlope}
                    onValueChange={setFaceSlope}
                    min={45}
                    max={90}
                    step={5}
                    data-testid="slider-face-slope"
                  />
                </div>

                <div className="pt-4 border-t">
                  <div className="flex items-center gap-2 mb-3">
                    {isADACompliant ? (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-medium text-green-600">ADA Compliant</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-5 w-5 text-red-600" />
                        <span className="text-sm font-medium text-red-600">Non-Compliant</span>
                      </>
                    )}
                  </div>
                  {!isADACompliant && (
                    <p className="text-xs text-muted-foreground">
                      Barrier curbs must be ≥6" for accessible route separation
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Material Specs</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <Label className="text-sm">Concrete Strength</Label>
                  <Select value={concreteStrength} onValueChange={setConcreteStrength}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3000">3000 psi</SelectItem>
                      <SelectItem value="3500">3500 psi</SelectItem>
                      <SelectItem value="4000">4000 psi</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm">Finish</Label>
                  <Select value={finish} onValueChange={setFinish}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="broom">Broom Finish</SelectItem>
                      <SelectItem value="smooth">Smooth Trowel</SelectItem>
                      <SelectItem value="exposed">Exposed Aggregate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="pt-3 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Estimated Cost:</span>
                    <span className="font-mono font-semibold text-lg">${estimatedCost()}/LF</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Visual Preview */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Profile Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-muted/30 rounded-lg p-8">
                  <svg viewBox="0 0 400 200" className="w-full h-64">
                    {/* Street surface */}
                    <rect x="0" y="150" width="200" height="50" fill="currentColor" className="text-gray-400" />
                    
                    {/* Curb profile based on type */}
                    {curbType === 'barrier' && (
                      <polygon
                        points={`200,150 200,${150 - height[0] * 8} 212,${150 - height[0] * 8} 212,150`}
                        fill="currentColor"
                        className="text-gray-600"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                    )}
                    
                    {curbType === 'mountable' && (
                      <polygon
                        points={`200,150 188,${150 - height[0] * 8} 212,${150 - height[0] * 8} 224,150`}
                        fill="currentColor"
                        className="text-gray-600"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                    )}

                    {curbType === 'rolled' && (
                      <path
                        d={`M 200 150 Q 194 ${150 - height[0] * 8} 206 ${150 - height[0] * 8} Q 218 ${150 - height[0] * 8} 224 150`}
                        fill="currentColor"
                        className="text-gray-600"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                    )}

                    {curbType === 'integral' && (
                      <>
                        <polygon
                          points={`170,150 170,${150 - height[0] * 8} 182,${150 - height[0] * 8} 182,150`}
                          fill="currentColor"
                          className="text-gray-600"
                          stroke="currentColor"
                          strokeWidth="2"
                        />
                        <rect x="182" y="145" width="60" height="5" fill="currentColor" className="text-gray-600" />
                      </>
                    )}
                    
                    {/* Sidewalk */}
                    <rect x="212" y="150" width="188" height="50" fill="currentColor" className="text-gray-300" />
                    
                    {/* Dimension lines */}
                    <line x1="200" y1="140" x2="200" y2={140 - height[0] * 8} stroke="blue" strokeWidth="1" strokeDasharray="2,2" />
                    <text x="180" y={145 - height[0] * 4} className="text-xs fill-blue-600" textAnchor="end">
                      {height[0]}"
                    </text>
                    
                    {/* Labels */}
                    <text x="100" y="180" className="text-xs fill-current" textAnchor="middle">Street</text>
                    <text x="306" y="180" className="text-xs fill-current" textAnchor="middle">Sidewalk</text>
                  </svg>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="library">
              <TabsList className="w-full">
                <TabsTrigger value="library" className="flex-1">Curb Library</TabsTrigger>
                <TabsTrigger value="details" className="flex-1">Detail References</TabsTrigger>
              </TabsList>
              
              <TabsContent value="library" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-2">
                    {curbTypes.map((curb) => (
                      <div key={curb.id} className="flex items-center justify-between p-3 border rounded hover-elevate">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono text-sm">{curb.id}</span>
                            <span className="font-medium">{curb.name}</span>
                            {curb.adaCompliant && (
                              <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                ADA
                              </Badge>
                            )}
                          </div>
                          <div className="grid grid-cols-4 gap-3 text-sm text-muted-foreground">
                            <span>H: {curb.height}"</span>
                            <span>W: {curb.width}"</span>
                            <span>{curb.material}</span>
                            <span>${curb.costPerLF}/LF</span>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => applyCurbTemplate(curb)}
                          data-testid={`button-apply-${curb.id}`}
                        >
                          Apply
                        </Button>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="details" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-2">
                    <div className="flex justify-between items-center p-3 border rounded">
                      <span className="font-medium">Standard Curb Detail</span>
                      <span className="font-mono text-sm text-muted-foreground">D-6.1</span>
                    </div>
                    <div className="flex justify-between items-center p-3 border rounded">
                      <span className="font-medium">Curb Ramp Detail</span>
                      <span className="font-mono text-sm text-muted-foreground">D-6.2</span>
                    </div>
                    <div className="flex justify-between items-center p-3 border rounded">
                      <span className="font-medium">Integral C&G Detail</span>
                      <span className="font-mono text-sm text-muted-foreground">D-6.3</span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        <div className="flex gap-2">
          <Button data-testid="button-save-curb">Save Curb Type</Button>
          <Button variant="outline" data-testid="button-export-curb">Export to Library</Button>
        </div>
      </div>
    </div>
  );
}
