import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';
import { Layers, AlertOctagon, CheckCircle, Shield, Zap, FileDown } from 'lucide-react';

type Clash = {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  type: string;
  element1: string;
  element2: string;
  description: string;
  location: string;
  autoSuggestion?: string;
  resolved: boolean;
};

export default function ClashDetection() {
  const exportToJSON = () => {
    const data = {
      project: 'Clash Detection Report',
      clashes,
      unresolvedCount: clashes.filter(c => !c.resolved).length,
      criticalCount: clashes.filter(c => c.severity === 'critical' && !c.resolved).length,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'clash_report.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    let csv = 'Severity,Type,Element 1,Element 2,Description,Location,Auto-Suggestion,Resolved\n';
    clashes.forEach(c => {
      csv += `${c.severity},${c.type},"${c.element1}","${c.element2}","${c.description}","${c.location}","${c.autoSuggestion || ''}",${c.resolved}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'clash_report.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const [clashes, setClashes] = useState<Clash[]>([
    {
      id: '1',
      severity: 'critical',
      type: 'Spatial Conflict',
      element1: 'Storm Pipe P-7',
      element2: 'Water Main WM-3',
      description: 'Pipe crossing with insufficient clearance (2.1\' actual, 3.0\' required)',
      location: 'Station 2+45',
      autoSuggestion: 'Lower storm pipe invert by 1.0\' or reroute water main',
      resolved: false
    },
    {
      id: '2',
      severity: 'critical',
      type: 'Spatial Conflict',
      element1: 'Sanitary Sewer SS-4',
      element2: 'Building Foundation',
      description: 'Sewer line passes through proposed building footprint',
      location: 'Station 1+78',
      autoSuggestion: 'Reroute sanitary sewer to avoid building',
      resolved: false
    },
    {
      id: '3',
      severity: 'warning',
      type: 'Clearance Issue',
      element1: 'Storm Inlet SI-2',
      element2: 'Proposed Tree',
      description: 'Inlet within 5\' of tree critical root zone',
      location: 'Grid B-3',
      autoSuggestion: 'Relocate inlet 3\' east',
      resolved: false
    },
    {
      id: '4',
      severity: 'warning',
      type: 'Clearance Issue',
      element1: 'Electrical Conduit',
      element2: 'Storm Pipe P-3',
      description: 'Minimal horizontal separation (3.2\' actual, 3.0\' min)',
      location: 'Station 0+85',
      resolved: false
    },
    {
      id: '5',
      severity: 'info',
      type: 'Best Practice',
      element1: 'Fire Hydrant FH-2',
      element2: 'ADA Parking',
      description: 'Fire hydrant within 6\' of accessible space (recommend 10\' min)',
      location: 'Parking Lot Area A',
      autoSuggestion: 'Shift hydrant 5\' north',
      resolved: true
    },
  ]);

  const [autoResolve, setAutoResolve] = useState(true);
  const [realTimeCheck, setRealTimeCheck] = useState(true);

  const toggleResolve = (id: string) => {
    setClashes(clashes.map(clash =>
      clash.id === id ? { ...clash, resolved: !clash.resolved } : clash
    ));
  };

  const applySuggestion = (id: string) => {
    console.log('Applying auto-suggestion for clash:', id);
    toggleResolve(id);
  };

  const runClashDetection = () => {
    console.log('Running clash detection...');
  };

  const unresolvedCount = clashes.filter(c => !c.resolved).length;
  const criticalCount = clashes.filter(c => c.severity === 'critical' && !c.resolved).length;

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Layers className="h-8 w-8 text-red-600" />
              <h1 className="text-3xl font-bold">Clash Detection</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Real-time spatial conflict analysis
            </p>
          </div>
          <Badge variant="outline">Concept</Badge>
        </div>

        {/* Key Concept Banner */}
        <Card className="border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Shield className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900 dark:text-red-100">Spatial Intelligence, Not Visual Checking</p>
                <p className="text-sm text-red-800 dark:text-red-200 mt-1">
                  Every element in the database has 3D geometry and defined clearance requirements. The system continuously 
                  checks for conflicts - utility crossings, root zone interference, ADA compliance - the moment you place an object.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Banner */}
        {criticalCount > 0 && (
          <Card className="border-red-500 bg-red-50 dark:bg-red-950/30">
            <CardContent className="pt-4 pb-4">
              <div className="flex items-center gap-3">
                <AlertOctagon className="h-6 w-6 text-red-600" />
                <div>
                  <p className="font-semibold text-red-900 dark:text-red-100">
                    {criticalCount} Critical Conflicts Detected
                  </p>
                  <p className="text-sm text-red-800 dark:text-red-200">
                    These must be resolved before proceeding with design
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-3 gap-6">
          {/* Clashes List */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Detected Conflicts</CardTitle>
                  <div className="flex gap-2">
                    <Badge variant="destructive">{unresolvedCount} unresolved</Badge>
                    <Button size="sm" onClick={runClashDetection} data-testid="button-run-detection">
                      <Zap className="h-4 w-4 mr-2" />
                      Re-Run Check
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {clashes.map((clash) => (
                  <Card
                    key={clash.id}
                    className={clash.resolved ? 'opacity-60' : ''}
                  >
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant={
                              clash.severity === 'critical' ? 'destructive' :
                              clash.severity === 'warning' ? 'secondary' : 'outline'
                            } className="text-xs">
                              {clash.severity}
                            </Badge>
                            <span className="text-sm font-medium">{clash.type}</span>
                            {clash.resolved && (
                              <Badge className="bg-green-600 text-xs">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Resolved
                              </Badge>
                            )}
                          </div>

                          <div className="space-y-1 text-sm">
                            <p>
                              <span className="font-medium">{clash.element1}</span>
                              {' ↔ '}
                              <span className="font-medium">{clash.element2}</span>
                            </p>
                            <p className="text-muted-foreground">{clash.description}</p>
                            <p className="text-xs text-muted-foreground">Location: {clash.location}</p>
                          </div>

                          {clash.autoSuggestion && !clash.resolved && (
                            <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-950/20 rounded border border-blue-200 dark:border-blue-900">
                              <div className="flex items-start gap-2">
                                <Zap className="h-4 w-4 text-blue-600 mt-0.5" />
                                <div className="flex-1">
                                  <p className="text-xs font-medium text-blue-900 dark:text-blue-100">AI Suggestion:</p>
                                  <p className="text-xs text-blue-800 dark:text-blue-200">{clash.autoSuggestion}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="flex gap-1 ml-4">
                          {clash.autoSuggestion && !clash.resolved && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => applySuggestion(clash.id)}
                              data-testid={`button-apply-${clash.id}`}
                            >
                              Apply Fix
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant={clash.resolved ? 'outline' : 'default'}
                            onClick={() => toggleResolve(clash.id)}
                            data-testid={`button-resolve-${clash.id}`}
                          >
                            {clash.resolved ? 'Reopen' : 'Mark Resolved'}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detection Rules</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="utilities">
                  <TabsList className="w-full">
                    <TabsTrigger value="utilities" className="flex-1">Utilities</TabsTrigger>
                    <TabsTrigger value="site" className="flex-1">Site Features</TabsTrigger>
                    <TabsTrigger value="standards" className="flex-1">Standards</TabsTrigger>
                  </TabsList>

                  <TabsContent value="utilities" className="mt-4 space-y-2">
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Pipe-to-Pipe Clearance</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">Min 3.0' horizontal, 1.0' vertical</p>
                    </div>
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Utility-to-Structure</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">Min 5.0' from building foundations</p>
                    </div>
                  </TabsContent>

                  <TabsContent value="site" className="mt-4 space-y-2">
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Tree Protection</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">Critical root zone = 1' per 1" DBH</p>
                    </div>
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">ADA Clearances</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">5' min accessible route width</p>
                    </div>
                  </TabsContent>

                  <TabsContent value="standards" className="mt-4 space-y-2">
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">VDOT Road Design</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">2021 Standards applied</p>
                    </div>
                    <div className="p-3 border rounded">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Local Fire Access</span>
                        <Badge className="bg-green-600">Active</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">24' min fire lane width</p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Settings & Summary */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detection Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm">Real-Time Checking</Label>
                    <Checkbox
                      checked={realTimeCheck}
                      onCheckedChange={(checked) => setRealTimeCheck(!!checked)}
                      data-testid="checkbox-realtime"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Continuously check for conflicts as you edit
                  </p>
                </div>

                <div className="space-y-3 pt-3 border-t">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm">Auto-Resolution</Label>
                    <Checkbox
                      checked={autoResolve}
                      onCheckedChange={(checked) => setAutoResolve(!!checked)}
                      data-testid="checkbox-autoresolve"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Automatically apply AI-suggested fixes when safe
                  </p>
                </div>

                <div className="pt-3 border-t">
                  <Button variant="outline" className="w-full" size="sm">
                    Configure Rules
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">3D Clash View</CardTitle>
              </CardHeader>
              <CardContent>
                {clashes.filter(c => !c.resolved).length > 0 ? (
                  <>
                    <div className="bg-card border rounded-lg" data-testid="clash-3d-view">
                      {(() => {
                        const activeClash = clashes.find(c => !c.resolved) || clashes[0];
                        const clearanceMatch = activeClash.description.match(/(\d+\.\d+)'\s+actual,\s+(\d+\.\d+)'\s+required/);
                        const actualClearance = clearanceMatch ? clearanceMatch[1] : '2.1';
                        const requiredClearance = clearanceMatch ? clearanceMatch[2] : '3.0';
                        
                        return (
                          <svg viewBox="0 0 300 280" className="w-full h-full">
                            {/* Isometric grid */}
                            <g opacity="0.1">
                              <line x1="50" y1="240" x2="250" y2="240" stroke="currentColor" className="text-muted-foreground" strokeWidth="0.5" />
                              <line x1="50" y1="220" x2="250" y2="220" stroke="currentColor" className="text-muted-foreground" strokeWidth="0.5" />
                              <line x1="50" y1="200" x2="250" y2="200" stroke="currentColor" className="text-muted-foreground" strokeWidth="0.5" />
                            </g>

                            {/* Title */}
                            <text x="10" y="20" fontSize="11" fontWeight="bold" fill="currentColor" className="text-muted-foreground">
                              {activeClash.element1} ↔ {activeClash.element2}
                            </text>

                            {/* Element 1 (blue - horizontal at depth) */}
                            <g>
                              <path 
                                d="M 40,140 L 260,140 L 260,150 L 40,150 Z" 
                                fill="hsl(221 83% 53%)" 
                                opacity="0.8"
                              />
                              <path 
                                d="M 40,140 L 50,130 L 270,130 L 260,140 Z" 
                                fill="hsl(221 83% 53%)" 
                                opacity="0.9"
                              />
                              
                              <text x="150" y="165" fontSize="8" fontWeight="bold" fill="hsl(221 83% 53%)" textAnchor="middle">
                                {activeClash.element1}
                              </text>
                            </g>

                            {/* Element 2 (green - crossing above/perpendicular) */}
                            <g>
                              <ellipse cx="150" cy="100" rx="6" ry="20" fill="hsl(142 76% 36%)" opacity="0.8" />
                              <rect x="144" y="80" width="12" height="40" fill="hsl(142 76% 36%)" opacity="0.8" />
                              
                              <text x="180" y="100" fontSize="8" fontWeight="bold" fill="hsl(142 76% 36%)" textAnchor="start">
                                {activeClash.element2}
                              </text>
                            </g>

                            {/* Clearance zone (conflict) */}
                            <g>
                              <ellipse cx="150" cy="120" rx="30" ry="50" fill="hsl(0 84% 60%)" opacity="0.15" />
                              <ellipse cx="150" cy="120" rx="30" ry="50" fill="none" stroke="hsl(0 84% 60%)" strokeWidth="2" strokeDasharray="4,2" />
                              
                              <circle cx="150" cy="120" r="8" fill="hsl(0 84% 60%)" />
                              <text x="150" y="124" fontSize="10" fontWeight="bold" fill="white" textAnchor="middle">!</text>
                            </g>

                            {/* Measurements */}
                            <g>
                              <line x1="25" y1="100" x2="25" y2="140" stroke="hsl(0 84% 60%)" strokeWidth="1" />
                              <line x1="20" y1="100" x2="30" y2="100" stroke="hsl(0 84% 60%)" strokeWidth="1" />
                              <line x1="20" y1="140" x2="30" y2="140" stroke="hsl(0 84% 60%)" strokeWidth="1" />
                              <text x="15" y="123" fontSize="9" fontWeight="bold" fill="hsl(0 84% 60%)" textAnchor="end">{actualClearance}'</text>
                              
                              <text x="150" y="200" fontSize="8" fill="hsl(0 84% 60%)" className="font-bold" textAnchor="middle">
                                {activeClash.type}
                              </text>
                              <text x="150" y="210" fontSize="7" fill="currentColor" className="text-muted-foreground" textAnchor="middle">
                                Actual: {actualClearance}' • Required: {requiredClearance}'
                              </text>
                            </g>

                            {/* Legend */}
                            <g transform="translate(10, 250)">
                              <rect x="0" y="0" width="12" height="8" fill="hsl(221 83% 53%)" opacity="0.8" />
                              <text x="16" y="6" fontSize="7" fill="currentColor" className="text-muted-foreground">{activeClash.element1.split(' ')[0]}</text>
                              
                              <rect x="80" y="0" width="12" height="8" fill="hsl(142 76% 36%)" opacity="0.8" />
                              <text x="96" y="6" fontSize="7" fill="currentColor" className="text-muted-foreground">{activeClash.element2.split(' ')[0]}</text>
                              
                              <circle cx="166" cy="4" r="4" fill="none" stroke="hsl(0 84% 60%)" strokeWidth="1" strokeDasharray="2,1" />
                              <text x="174" y="6" fontSize="7" fill="currentColor" className="text-muted-foreground">Conflict</text>
                            </g>

                            {/* Location marker */}
                            <text x="150" y="235" fontSize="7" fill="currentColor" className="text-muted-foreground" textAnchor="middle">
                              {activeClash.location}
                            </text>
                          </svg>
                        );
                      })()}
                    </div>
                    <p className="text-xs text-muted-foreground text-center mt-2">
                      {unresolvedCount} conflicts • Real-time spatial analysis
                    </p>
                  </>
                ) : (
                  <div className="bg-muted/30 rounded-lg p-8 text-center">
                    <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
                    <p className="font-medium">No Active Conflicts</p>
                    <p className="text-sm text-muted-foreground mt-1">All clashes have been resolved</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export Clash Report</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full" size="sm" onClick={exportToJSON} data-testid="button-export-json">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Report (JSON)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToCSV} data-testid="button-export-csv">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Conflicts (CSV)
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="p-3 border-l-4 border-l-red-500 bg-red-50 dark:bg-red-950/20 rounded">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Critical</span>
                    <Badge variant="destructive">{criticalCount}</Badge>
                  </div>
                </div>

                <div className="p-3 border-l-4 border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950/20 rounded">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Warnings</span>
                    <Badge variant="secondary">
                      {clashes.filter(c => c.severity === 'warning' && !c.resolved).length}
                    </Badge>
                  </div>
                </div>

                <div className="p-3 border-l-4 border-l-blue-500 bg-blue-50 dark:bg-blue-950/20 rounded">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Info</span>
                    <Badge variant="outline">
                      {clashes.filter(c => c.severity === 'info' && !c.resolved).length}
                    </Badge>
                  </div>
                </div>

                <div className="pt-3 border-t">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Total Resolved:</span>
                    <span className="font-medium">{clashes.filter(c => c.resolved).length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full" size="sm">
                  Export Clash Report
                </Button>
                <Button variant="outline" className="w-full" size="sm">
                  Generate 3D View
                </Button>
                <Button className="w-full" size="sm">
                  Send to Team
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
