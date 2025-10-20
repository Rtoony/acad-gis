import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { useState } from 'react';
import { Wand2, Zap, TrendingUp, RefreshCw, FileDown } from 'lucide-react';

type Solution = {
  id: number;
  name: string;
  score: number;
  spaces: number;
  driveAisleWidth: number;
  angleCount: number;
  cost: string;
  notes: string;
};

export default function ConstraintSolver() {
  const [minSpaces, setMinSpaces] = useState([120]);
  const [targetSpaces, setTargetSpaces] = useState([135]);
  const [adaCompliance, setAdaCompliance] = useState(true);
  const [fireAccess, setFireAccess] = useState(true);
  const [snowStorage, setSnowStorage] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [solutions, setSolutions] = useState<Solution[]>([
    {
      id: 1,
      name: 'Optimize for Maximum Spaces',
      score: 92,
      spaces: 138,
      driveAisleWidth: 24,
      angleCount: 45,
      cost: 'Medium',
      notes: 'Uses 45° angled parking for efficient space use'
    },
    {
      id: 2,
      name: 'Balance Cost & Capacity',
      score: 88,
      spaces: 132,
      driveAisleWidth: 26,
      angleCount: 60,
      cost: 'Low',
      notes: 'Wider aisles for better circulation'
    },
    {
      id: 3,
      name: 'Pedestrian-Friendly Layout',
      score: 85,
      spaces: 128,
      driveAisleWidth: 28,
      angleCount: 90,
      cost: 'High',
      notes: 'Perpendicular parking with landscape islands'
    },
  ]);

  const generateSolutions = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setSolutions([
        {
          id: 1,
          name: 'AI-Optimized Maximum Density',
          score: 95,
          spaces: 142,
          driveAisleWidth: 24,
          angleCount: 45,
          cost: 'Medium',
          notes: 'Hybrid 45°/60° layout maximizing site geometry'
        },
        {
          id: 2,
          name: 'Fire Lane Priority',
          score: 91,
          spaces: 136,
          driveAisleWidth: 26,
          angleCount: 60,
          cost: 'Medium',
          notes: 'Optimized fire truck access routes'
        },
        {
          id: 3,
          name: 'Snow Storage Compliant',
          score: 87,
          spaces: 130,
          driveAisleWidth: 28,
          angleCount: 90,
          cost: 'Low',
          notes: 'Dedicated snow storage areas integrated'
        },
      ]);
      setIsGenerating(false);
    }, 1500);
  };

  const exportToDXF = () => {
    const topSolution = solutions[0];
    let dxf = `0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n`;
    
    // Add parking stalls as rectangles
    for (let i = 0; i < Math.min(topSolution.spaces, 10); i++) {
      const x = (i % 5) * 20;
      const y = Math.floor(i / 5) * 40;
      dxf += `0\nLWPOLYLINE\n8\nPARKING\n90\n5\n70\n1\n43\n0\n10\n${x}\n20\n${y}\n10\n${x + 18}\n20\n${y}\n10\n${x + 18}\n20\n${y + 9}\n10\n${x}\n20\n${y + 9}\n10\n${x}\n20\n${y}\n`;
    }
    
    dxf += `0\nENDSEC\n0\nEOF\n`;
    
    const blob = new Blob([dxf], { type: 'application/dxf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `parking_layout_${topSolution.name.replace(/\s+/g, '_')}.dxf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToJSON = () => {
    const data = {
      constraints: {
        minSpaces: minSpaces[0],
        targetSpaces: targetSpaces[0],
        adaCompliance,
        fireAccess,
        snowStorage
      },
      solutions,
      generatedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parking_solutions.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    let csv = 'Solution,Score,Spaces,Drive Aisle Width,Angle,Cost,Notes\n';
    solutions.forEach(sol => {
      csv += `"${sol.name}",${sol.score},${sol.spaces},${sol.driveAisleWidth},${sol.angleCount}°,${sol.cost},"${sol.notes}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parking_solutions.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Wand2 className="h-8 w-8 text-indigo-600" />
              <h1 className="text-3xl font-bold">Constraint Solver</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              AI-powered parking lot layout optimizer
            </p>
          </div>
          <Badge variant="outline">Concept</Badge>
        </div>

        {/* Key Concept Banner */}
        <Card className="border-indigo-200 dark:border-indigo-900 bg-indigo-50 dark:bg-indigo-950/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Zap className="h-5 w-5 text-indigo-600 mt-0.5" />
              <div>
                <p className="font-medium text-indigo-900 dark:text-indigo-100">Constraint-Based Design</p>
                <p className="text-sm text-indigo-800 dark:text-indigo-200 mt-1">
                  Define your requirements (minimum spaces, ADA compliance, fire access) and let the AI generate multiple 
                  optimized solutions. Each solution automatically balances competing constraints - something impossible with traditional CAD.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-6">
          {/* Constraint Inputs */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Design Constraints</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Minimum Parking Spaces</Label>
                  <div className="flex items-center gap-3">
                    <Slider
                      value={minSpaces}
                      onValueChange={setMinSpaces}
                      min={80}
                      max={200}
                      step={1}
                      className="flex-1"
                      data-testid="slider-min-spaces"
                    />
                    <span className="text-sm font-medium w-12">{minSpaces[0]}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Target Spaces (Desired)</Label>
                  <div className="flex items-center gap-3">
                    <Slider
                      value={targetSpaces}
                      onValueChange={setTargetSpaces}
                      min={minSpaces[0]}
                      max={200}
                      step={1}
                      className="flex-1"
                      data-testid="slider-target-spaces"
                    />
                    <span className="text-sm font-medium w-12">{targetSpaces[0]}</span>
                  </div>
                </div>

                <div className="pt-3 border-t space-y-3">
                  <Label className="text-sm font-semibold">Required Compliance</Label>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={adaCompliance}
                        onCheckedChange={(checked) => setAdaCompliance(!!checked)}
                        data-testid="checkbox-ada"
                      />
                      <Label className="text-sm font-normal">ADA Accessible (5% minimum)</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={fireAccess}
                        onCheckedChange={(checked) => setFireAccess(!!checked)}
                        data-testid="checkbox-fire"
                      />
                      <Label className="text-sm font-normal">Fire Lane Access (26' wide)</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={snowStorage}
                        onCheckedChange={(checked) => setSnowStorage(!!checked)}
                        data-testid="checkbox-snow"
                      />
                      <Label className="text-sm font-normal">Snow Storage Areas</Label>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t space-y-2">
                  <Label>Site Area</Label>
                  <Input value="2.4 acres" readOnly className="bg-muted/50" />
                </div>

                <div className="space-y-2">
                  <Label>Available Area (After Setbacks)</Label>
                  <Input value="78,400 sq ft" readOnly className="bg-muted/50" />
                </div>

                <Button
                  onClick={generateSolutions}
                  disabled={isGenerating}
                  className="w-full"
                  data-testid="button-generate"
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Wand2 className="h-4 w-4 mr-2" />
                      Generate Solutions
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Generated Solutions */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>AI-Generated Solutions</CardTitle>
                  <Badge>{solutions.length} options</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {solutions.map((solution) => (
                  <Card key={solution.id} className="hover-elevate cursor-pointer">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold">{solution.name}</h3>
                          <p className="text-sm text-muted-foreground mt-1">{solution.notes}</p>
                        </div>
                        <Badge className="ml-2" variant={solution.score >= 90 ? 'default' : 'secondary'}>
                          Score: {solution.score}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-4 gap-3 mt-4">
                        <div className="p-2 bg-muted/30 rounded">
                          <p className="text-xs text-muted-foreground">Spaces</p>
                          <p className="text-lg font-bold">{solution.spaces}</p>
                        </div>
                        <div className="p-2 bg-muted/30 rounded">
                          <p className="text-xs text-muted-foreground">Aisle Width</p>
                          <p className="text-lg font-bold">{solution.driveAisleWidth}'</p>
                        </div>
                        <div className="p-2 bg-muted/30 rounded">
                          <p className="text-xs text-muted-foreground">Angle</p>
                          <p className="text-lg font-bold">{solution.angleCount}°</p>
                        </div>
                        <div className="p-2 bg-muted/30 rounded">
                          <p className="text-xs text-muted-foreground">Cost</p>
                          <p className="text-lg font-bold">{solution.cost}</p>
                        </div>
                      </div>

                      <div className="flex gap-2 mt-4">
                        <Button size="sm" variant="outline" className="flex-1">
                          Preview Layout
                        </Button>
                        <Button size="sm" className="flex-1" data-testid={`button-apply-${solution.id}`}>
                          Apply to Site
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export Solutions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full" size="sm" onClick={exportToDXF} data-testid="button-export-dxf">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Layout (DXF)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToJSON} data-testid="button-export-json">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Solutions (JSON)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToCSV} data-testid="button-export-csv">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Comparison (CSV)
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Layout Visualization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-card border rounded-lg" data-testid="parking-layout-view">
                  <svg viewBox="0 0 400 300" className="w-full h-full">
                    {/* Site boundary */}
                    <rect x="10" y="10" width="380" height="280" fill="none" stroke="currentColor" strokeWidth="2" className="text-border" strokeDasharray="6,3" />
                    
                    {/* Fire lane */}
                    {fireAccess && (
                      <g>
                        <rect x="20" y="20" width="360" height="30" fill="hsl(0 84% 60%)" opacity="0.2" stroke="hsl(0 84% 60%)" strokeWidth="1.5" />
                        <text x="200" y="38" fontSize="9" fill="hsl(0 84% 60%)" className="font-bold" textAnchor="middle">FIRE LANE - NO PARKING</text>
                      </g>
                    )}
                    
                    {/* Main parking rows - left side */}
                    {(() => {
                      const topSolution = solutions[0];
                      const angle = topSolution.angleCount;
                      const stallCount = Math.floor(topSolution.spaces * 0.4);
                      
                      return (
                        <g>
                          {/* Left parking row */}
                          {[...Array(Math.min(10, stallCount / 2))].map((_, i) => (
                            <g key={`left-${i}`}>
                              <rect 
                                x={30} 
                                y={70 + i * 20} 
                                width={angle === 90 ? 18 : 22} 
                                height={16} 
                                fill="none" 
                                stroke="currentColor" 
                                strokeWidth="1" 
                                className="text-foreground"
                                transform={angle !== 90 ? `rotate(${angle - 90} ${30 + 11} ${78 + i * 20})` : ''}
                              />
                            </g>
                          ))}
                          
                          {/* Right parking row */}
                          {[...Array(Math.min(10, stallCount / 2))].map((_, i) => (
                            <g key={`right-${i}`}>
                              <rect 
                                x={350} 
                                y={70 + i * 20} 
                                width={angle === 90 ? 18 : 22} 
                                height={16} 
                                fill="none" 
                                stroke="currentColor" 
                                strokeWidth="1" 
                                className="text-foreground"
                                transform={angle !== 90 ? `rotate(${90 - angle} ${350 + 11} ${78 + i * 20})` : ''}
                              />
                            </g>
                          ))}
                        </g>
                      );
                    })()}
                    
                    {/* Drive aisle */}
                    <g>
                      <line x1="80" y1="70" x2="80" y2="270" stroke="currentColor" strokeWidth="1" className="text-muted-foreground" strokeDasharray="8,4" />
                      <line x1="320" y1="70" x2="320" y2="270" stroke="currentColor" strokeWidth="1" className="text-muted-foreground" strokeDasharray="8,4" />
                      <text x="200" y="175" fontSize="10" fill="currentColor" className="text-muted-foreground font-mono" textAnchor="middle">
                        {solutions[0]?.driveAisleWidth}' DRIVE AISLE
                      </text>
                    </g>
                    
                    {/* ADA spaces */}
                    {adaCompliance && (
                      <g>
                        <rect x="30" y="70" width="18" height="16" fill="hsl(221 83% 53%)" opacity="0.3" stroke="hsl(221 83% 53%)" strokeWidth="2" />
                        <text x="39" y="81" fontSize="8" fill="hsl(221 83% 53%)" className="font-bold" textAnchor="middle">♿</text>
                        <rect x="30" y="90" width="18" height="16" fill="hsl(221 83% 53%)" opacity="0.3" stroke="hsl(221 83% 53%)" strokeWidth="2" />
                        <text x="39" y="101" fontSize="8" fill="hsl(221 83% 53%)" className="font-bold" textAnchor="middle">♿</text>
                      </g>
                    )}
                    
                    {/* Snow storage area */}
                    {snowStorage && (
                      <g>
                        <rect x="100" y="260" width="200" height="20" fill="hsl(200 98% 39%)" opacity="0.2" stroke="hsl(200 98% 39%)" strokeWidth="1" strokeDasharray="3,3" />
                        <text x="200" y="273" fontSize="8" fill="hsl(200 98% 39%)" className="font-mono" textAnchor="middle">SNOW STORAGE</text>
                      </g>
                    )}
                    
                    {/* Dimensions */}
                    <g>
                      <line x1="80" y1="55" x2="320" y2="55" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <line x1="80" y1="50" x2="80" y2="60" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <line x1="320" y1="50" x2="320" y2="60" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <text x="200" y="50" fontSize="7" fill="currentColor" className="text-muted-foreground font-mono" textAnchor="middle">
                        {solutions[0]?.driveAisleWidth}'
                      </text>
                    </g>
                    
                    {/* Labels */}
                    <text x="395" y="15" fontSize="8" fill="currentColor" className="text-muted-foreground font-mono" textAnchor="end">
                      {solutions[0]?.spaces} SPACES • {solutions[0]?.angleCount}° ANGLE
                    </text>
                  </svg>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">
                  Top solution preview • {solutions[0]?.name}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Optimization Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 border rounded">
                    <TrendingUp className="h-6 w-6 mx-auto text-green-600 mb-2" />
                    <p className="text-2xl font-bold">{solutions[0]?.spaces || 138}</p>
                    <p className="text-xs text-muted-foreground">Best Space Count</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <TrendingUp className="h-6 w-6 mx-auto text-blue-600 mb-2" />
                    <p className="text-2xl font-bold">{solutions[0]?.score || 92}%</p>
                    <p className="text-xs text-muted-foreground">Highest Score</p>
                  </div>
                  <div className="text-center p-3 border rounded">
                    <TrendingUp className="h-6 w-6 mx-auto text-purple-600 mb-2" />
                    <p className="text-2xl font-bold">3</p>
                    <p className="text-xs text-muted-foreground">Valid Layouts</p>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-muted/30 rounded text-sm">
                  <p className="font-medium mb-1">AI Optimization Factors:</p>
                  <ul className="text-xs text-muted-foreground space-y-1 ml-4 list-disc">
                    <li>Maximizing parking count within buildable area</li>
                    <li>Meeting ADA requirements (7 accessible spaces minimum)</li>
                    <li>Ensuring fire truck turning radius compliance</li>
                    <li>Optimizing circulation and pedestrian safety</li>
                    <li>Balancing construction cost vs. capacity</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
