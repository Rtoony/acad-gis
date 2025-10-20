import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';
import { FileOutput, Check, Mail, Upload, FileDown } from 'lucide-react';

export default function PlotProfileManager() {
  const [jobName, setJobName] = useState('90% Permit Submittal');
  const [selectedFormats, setSelectedFormats] = useState({
    pdf: true,
    dwg: false,
    landxml: true,
    svg: false
  });
  const [profile, setProfile] = useState('fairfax_swm');
  const [destination, setDestination] = useState({
    saveLocal: true,
    email: true,
    portal: false
  });
  const [emailAddress, setEmailAddress] = useState('jane.doe@county.gov');

  const profiles = [
    {
      id: 'fairfax_swm',
      name: 'Fairfax County SWM Permit',
      sheetSize: '24×36',
      lineWeights: 'VDOT Standard',
      titleBlock: 'Auto-populate',
      watermark: 'PRELIMINARY',
    },
    {
      id: 'client_review',
      name: 'Client Review Plot',
      sheetSize: '11×17',
      lineWeights: 'Standard',
      titleBlock: 'Simplified',
      watermark: 'FOR REVIEW ONLY',
    },
    {
      id: 'construction',
      name: 'Construction Documents',
      sheetSize: '24×36',
      lineWeights: 'Heavy',
      titleBlock: 'Full Detail',
      watermark: 'None',
    },
  ];

  const currentProfile = profiles.find(p => p.id === profile);

  const exportToDXF = () => {
    let dxf = `0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n1\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n`;
    dxf += `0\nTEXT\n8\n0\n10\n100\n20\n100\n40\n12\n1\n${jobName}\n0\nTEXT\n8\n0\n10\n100\n20\n80\n40\n8\n1\nProfile: ${currentProfile?.name}\n`;
    dxf += `0\nENDSEC\n0\nEOF\n`;
    
    const blob = new Blob([dxf], { type: 'application/dxf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${jobName.replace(/\s+/g, '_')}.dxf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToJSON = () => {
    const data = {
      jobName,
      profile: currentProfile,
      selectedFormats,
      destination,
      exportDate: new Date().toISOString(),
      sheetSettings: {
        size: currentProfile?.sheetSize,
        lineWeights: currentProfile?.lineWeights,
        titleBlock: currentProfile?.titleBlock,
        watermark: currentProfile?.watermark
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${jobName.replace(/\s+/g, '_')}_plot_config.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToSVG = () => {
    const svgElement = document.querySelector('[data-testid="sheet-layout-preview"] svg');
    if (!svgElement) return;
    
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${jobName.replace(/\s+/g, '_')}_layout.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <FileOutput className="h-8 w-8 text-emerald-600" />
              <h1 className="text-3xl font-bold">Plot & Export Manager</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Direct PDF/LandXML export without CAD engine
            </p>
          </div>
          <Badge variant="outline">Concept</Badge>
        </div>

        {/* Key Concept Banner */}
        <Card className="border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <FileOutput className="h-5 w-5 text-emerald-600 mt-0.5" />
              <div>
                <p className="font-medium text-emerald-900 dark:text-emerald-100">Bypassing the CAD Engine</p>
                <p className="text-sm text-emerald-800 dark:text-emerald-200 mt-1">
                  The database holds pure vector and property data - it doesn't need AutoCAD's plotting engine. 
                  Generate PDFs, LandXML, SVG, or any format directly from the database using modern open-source libraries.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-6">
          {/* Export Configuration */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Export Job Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Job Name</Label>
                  <Input
                    value={jobName}
                    onChange={(e) => setJobName(e.target.value)}
                    data-testid="input-job-name"
                  />
                </div>

                {/* Content Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold">Select Content</Label>
                  <div className="space-y-2 ml-3">
                    <div className="flex items-center gap-2">
                      <Checkbox defaultChecked data-testid="checkbox-sheet-set" />
                      <Label className="text-sm font-normal">Sheet Set: "Permit Set" (12 sheets)</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox defaultChecked data-testid="checkbox-report" />
                      <Label className="text-sm font-normal">Report: "Stormwater Management Report"</Label>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox defaultChecked data-testid="checkbox-network-data" />
                      <Label className="text-sm font-normal">Data: "Proposed Storm Network (LandXML)"</Label>
                    </div>
                  </div>
                </div>

                {/* Output Formats */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold">Select Output Format</Label>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={selectedFormats.pdf}
                        onCheckedChange={(checked) => setSelectedFormats({...selectedFormats, pdf: !!checked})}
                        data-testid="checkbox-pdf"
                      />
                      <div>
                        <Label className="text-sm font-normal">PDF</Label>
                        <p className="text-xs text-muted-foreground">Multi-page, combined</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={selectedFormats.dwg}
                        onCheckedChange={(checked) => setSelectedFormats({...selectedFormats, dwg: !!checked})}
                        data-testid="checkbox-dwg"
                      />
                      <div>
                        <Label className="text-sm font-normal">DWG</Label>
                        <p className="text-xs text-muted-foreground">For consultant</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={selectedFormats.landxml}
                        onCheckedChange={(checked) => setSelectedFormats({...selectedFormats, landxml: !!checked})}
                        data-testid="checkbox-landxml"
                      />
                      <div>
                        <Label className="text-sm font-normal">LandXML</Label>
                        <p className="text-xs text-muted-foreground">County review software</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={selectedFormats.svg}
                        onCheckedChange={(checked) => setSelectedFormats({...selectedFormats, svg: !!checked})}
                        data-testid="checkbox-svg"
                      />
                      <div>
                        <Label className="text-sm font-normal">SVG</Label>
                        <p className="text-xs text-muted-foreground">Web/interactive</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Plot Profile */}
                <div className="space-y-2">
                  <Label>Apply Plot Profile</Label>
                  <Select value={profile} onValueChange={setProfile}>
                    <SelectTrigger data-testid="select-profile">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {profiles.map(p => (
                        <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {currentProfile && (
                    <div className="mt-3 p-3 bg-muted/30 rounded-lg text-sm space-y-1">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Sheet Size:</span>
                        <span className="font-medium">{currentProfile.sheetSize}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Line Weights:</span>
                        <span className="font-medium">{currentProfile.lineWeights}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Title Block:</span>
                        <span className="font-medium">{currentProfile.titleBlock}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Watermark:</span>
                        <span className="font-medium">{currentProfile.watermark}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Destination */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold">Destination</Label>
                  <div className="space-y-2 ml-3">
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={destination.saveLocal}
                        onCheckedChange={(checked) => setDestination({...destination, saveLocal: !!checked})}
                        data-testid="checkbox-save-local"
                      />
                      <Label className="text-sm font-normal">Save to Project Folder</Label>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Checkbox
                          checked={destination.email}
                          onCheckedChange={(checked) => setDestination({...destination, email: !!checked})}
                          data-testid="checkbox-email"
                        />
                        <Label className="text-sm font-normal">Email to:</Label>
                      </div>
                      {destination.email && (
                        <Input
                          value={emailAddress}
                          onChange={(e) => setEmailAddress(e.target.value)}
                          className="ml-6"
                          placeholder="recipient@example.com"
                          data-testid="input-email"
                        />
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={destination.portal}
                        onCheckedChange={(checked) => setDestination({...destination, portal: !!checked})}
                        data-testid="checkbox-portal"
                      />
                      <Label className="text-sm font-normal">Upload to Client Portal</Label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Button className="w-full" size="lg" data-testid="button-run-export">
              <FileOutput className="h-4 w-4 mr-2" />
              Run Export Job
            </Button>
          </div>

          {/* Job Summary & Profiles */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sheet Layout Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-card border rounded-lg" data-testid="sheet-preview">
                  <svg viewBox="0 0 360 240" className="w-full h-full">
                    {/* Sheet border */}
                    <rect x="5" y="5" width="350" height="230" fill="none" stroke="currentColor" strokeWidth="3" className="text-foreground" />
                    
                    {/* Inner border */}
                    <rect x="15" y="15" width="330" height="210" fill="none" stroke="currentColor" strokeWidth="1" className="text-border" />
                    
                    {/* Title Block */}
                    <rect x="15" y="185" width="330" height="40" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-border" />
                    
                    {/* Title Block Divisions */}
                    <line x1="15" y1="205" x2="345" y2="205" stroke="currentColor" strokeWidth="1" className="text-border" />
                    <line x1="245" y1="185" x2="245" y2="225" stroke="currentColor" strokeWidth="1" className="text-border" />
                    <line x1="295" y1="185" x2="295" y2="225" stroke="currentColor" strokeWidth="1" className="text-border" />
                    
                    {/* Title Block Text */}
                    <text x="130" y="198" fontSize="12" fontWeight="bold" fill="currentColor" className="text-foreground">
                      {currentProfile?.name || 'Sheet Layout'}
                    </text>
                    <text x="20" y="218" fontSize="8" fill="currentColor" className="text-muted-foreground">PROJECT: RIVERSIDE DEVELOPMENT</text>
                    <text x="250" y="198" fontSize="8" fill="currentColor" className="text-muted-foreground">SHEET:</text>
                    <text x="255" y="218" fontSize="10" fontWeight="bold" fill="currentColor" className="text-foreground">C-4.1</text>
                    <text x="300" y="198" fontSize="8" fill="currentColor" className="text-muted-foreground">DATE:</text>
                    <text x="303" y="218" fontSize="8" fill="currentColor" className="text-foreground">10/07/24</text>
                    
                    {/* Watermark */}
                    {currentProfile?.watermark && currentProfile.watermark !== 'None' && (
                      <text 
                        x="180" 
                        y="120" 
                        fontSize="36" 
                        fontWeight="bold" 
                        fill="currentColor" 
                        className="text-muted-foreground/20"
                        textAnchor="middle"
                        transform="rotate(-45 180 120)"
                      >
                        {currentProfile.watermark}
                      </text>
                    )}
                    
                    {/* Main Viewport Content - Site Plan */}
                    <g transform="translate(25, 25)">
                      {/* Road centerline */}
                      <line x1="40" y1="80" x2="300" y2="80" stroke="currentColor" strokeWidth="2" className="text-foreground" strokeDasharray="8,4" />
                      
                      {/* Curb lines */}
                      <line x1="40" y1="60" x2="300" y2="60" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      <line x1="40" y1="100" x2="300" y2="100" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      
                      {/* Storm structures */}
                      <circle cx="100" cy="80" r="5" fill="hsl(221 83% 53%)" />
                      <circle cx="170" cy="80" r="5" fill="hsl(221 83% 53%)" />
                      <circle cx="240" cy="80" r="5" fill="hsl(221 83% 53%)" />
                      
                      {/* Storm pipes */}
                      <line x1="100" y1="80" x2="170" y2="80" stroke="hsl(221 83% 53%)" strokeWidth="3" />
                      <line x1="170" y1="80" x2="240" y2="80" stroke="hsl(221 83% 53%)" strokeWidth="3" />
                      
                      {/* Property lines */}
                      <line x1="30" y1="40" x2="310" y2="40" stroke="currentColor" strokeWidth="1" className="text-muted-foreground" strokeDasharray="3,3" />
                      <line x1="30" y1="120" x2="310" y2="120" stroke="currentColor" strokeWidth="1" className="text-muted-foreground" strokeDasharray="3,3" />
                      
                      {/* Dimension lines */}
                      <line x1="50" y1="130" x2="150" y2="130" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <line x1="50" y1="125" x2="50" y2="135" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <line x1="150" y1="125" x2="150" y2="135" stroke="currentColor" strokeWidth="0.5" className="text-muted-foreground" />
                      <text x="100" y="145" fontSize="7" fill="currentColor" className="text-muted-foreground" textAnchor="middle">100.0'</text>
                      
                      {/* Labels */}
                      <text x="170" y="95" fontSize="7" fill="currentColor" className="text-foreground font-mono">18" RCP</text>
                      <text x="170" y="50" fontSize="8" fill="currentColor" className="text-foreground font-mono">MAIN STREET</text>
                    </g>
                    
                    {/* North Arrow */}
                    <g transform="translate(325, 30)">
                      <line x1="0" y1="15" x2="0" y2="0" stroke="currentColor" strokeWidth="1.5" className="text-foreground" markerEnd="url(#arrowhead)" />
                      <text x="5" y="5" fontSize="8" fill="currentColor" className="text-foreground">N</text>
                      <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                          <polygon points="0 0, 10 5, 0 10" fill="currentColor" className="text-foreground" />
                        </marker>
                      </defs>
                    </g>
                    
                    {/* Scale */}
                    <g transform="translate(25, 170)">
                      <text x="0" y="0" fontSize="7" fill="currentColor" className="text-muted-foreground">SCALE: 1"=20'</text>
                    </g>
                  </svg>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">
                  {currentProfile?.sheetSize} • {currentProfile?.lineWeights} weights
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Export</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full" size="sm" onClick={exportToDXF} data-testid="button-export-dxf">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export as DXF
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToSVG} data-testid="button-export-svg">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Layout (SVG)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToJSON} data-testid="button-export-json">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Config (JSON)
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Job Name:</span>
                    <span className="font-medium">{jobName}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Formats:</span>
                    <span className="font-medium">
                      {Object.entries(selectedFormats).filter(([_, v]) => v).length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Destinations:</span>
                    <span className="font-medium">
                      {Object.entries(destination).filter(([_, v]) => v).length}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t">
                  <p className="text-xs text-muted-foreground mb-2">Output Files:</p>
                  <div className="space-y-1">
                    {selectedFormats.pdf && (
                      <div className="flex items-center gap-2 text-xs">
                        <Check className="h-3 w-3 text-green-600" />
                        <span className="font-mono">permit_set.pdf</span>
                      </div>
                    )}
                    {selectedFormats.landxml && (
                      <div className="flex items-center gap-2 text-xs">
                        <Check className="h-3 w-3 text-green-600" />
                        <span className="font-mono">storm_network.xml</span>
                      </div>
                    )}
                    {selectedFormats.dwg && (
                      <div className="flex items-center gap-2 text-xs">
                        <Check className="h-3 w-3 text-green-600" />
                        <span className="font-mono">permit_set.dwg</span>
                      </div>
                    )}
                    {selectedFormats.svg && (
                      <div className="flex items-center gap-2 text-xs">
                        <Check className="h-3 w-3 text-green-600" />
                        <span className="font-mono">site_plan.svg</span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="recent">
              <TabsList className="w-full">
                <TabsTrigger value="recent" className="flex-1">Recent Jobs</TabsTrigger>
                <TabsTrigger value="profiles" className="flex-1">Profiles</TabsTrigger>
              </TabsList>
              
              <TabsContent value="recent" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-2">
                    <div className="p-3 border rounded hover-elevate cursor-pointer">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">60% Review Set</span>
                        <Badge variant="outline" className="text-xs">2 days ago</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">PDF + LandXML</p>
                    </div>
                    <div className="p-3 border rounded hover-elevate cursor-pointer">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Client Markup</span>
                        <Badge variant="outline" className="text-xs">5 days ago</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">PDF only</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="profiles" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-2">
                    {profiles.map(p => (
                      <div key={p.id} className="p-3 border rounded hover-elevate cursor-pointer">
                        <p className="text-sm font-medium">{p.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {p.sheetSize} · {p.lineWeights}
                        </p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
