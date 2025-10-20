import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';
import { FileStack, Layout, Sparkles, Grid3x3, FileDown } from 'lucide-react';

type Sheet = {
  id: string;
  number: string;
  title: string;
  scale: string;
  matchLines: string[];
  status: 'draft' | 'review' | 'approved';
};

export default function SheetSetCoordinator() {
  const [sheets, setSheets] = useState<Sheet[]>([
    { id: '1', number: 'C-1', title: 'Overall Site Plan', scale: '1"=40\'', matchLines: ['North', 'East'], status: 'approved' },
    { id: '2', number: 'C-2', title: 'Grading & Drainage Plan (North)', scale: '1"=20\'', matchLines: ['South', 'East'], status: 'review' },
    { id: '3', number: 'C-3', title: 'Grading & Drainage Plan (South)', scale: '1"=20\'', matchLines: ['North', 'East'], status: 'draft' },
    { id: '4', number: 'C-4', title: 'Utility Plan', scale: '1"=20\'', matchLines: ['West'], status: 'review' },
    { id: '5', number: 'C-5', title: 'Storm Drainage Profile', scale: 'H:1"=40\', V:1"=4\'', matchLines: [], status: 'approved' },
  ]);

  const [autoNumber, setAutoNumber] = useState(true);
  const [matchLineStyle, setMatchLineStyle] = useState('circle');

  const addSheet = () => {
    const nextNum = sheets.length + 1;
    setSheets([...sheets, {
      id: String(nextNum),
      number: `C-${nextNum}`,
      title: 'New Sheet',
      scale: '1"=20\'',
      matchLines: [],
      status: 'draft'
    }]);
  };

  const updateMatchLines = () => {
    // Simulate intelligent match line detection
    const updated = sheets.map(sheet => {
      if (sheet.title.includes('North')) {
        return { ...sheet, matchLines: ['South', 'East', 'West'] };
      }
      if (sheet.title.includes('South')) {
        return { ...sheet, matchLines: ['North', 'East', 'West'] };
      }
      return sheet;
    });
    setSheets(updated);
  };

  const exportToDXF = () => {
    let dxf = `0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n`;
    sheets.forEach((sheet, i) => {
      const y = i * 100;
      dxf += `0\nTEXT\n8\n0\n10\n10\n20\n${y}\n40\n12\n1\n${sheet.number} - ${sheet.title}\n`;
    });
    dxf += `0\nENDSEC\n0\nEOF\n`;
    
    const blob = new Blob([dxf], { type: 'application/dxf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sheet_index.dxf';
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToJSON = () => {
    const data = {
      project: 'Sheet Set',
      sheets,
      settings: { autoNumber, matchLineStyle }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sheet_set.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    let csv = 'Number,Title,Scale,Match Lines,Status\n';
    sheets.forEach(s => {
      csv += `${s.number},"${s.title}",${s.scale},"${s.matchLines.join(', ')}",${s.status}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sheet_set.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <FileStack className="h-8 w-8 text-pink-600" />
              <h1 className="text-3xl font-bold">Sheet Set Coordinator</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Smart match lines and automatic sheet numbering
            </p>
          </div>
          <Badge variant="outline">Concept</Badge>
        </div>

        {/* Key Concept Banner */}
        <Card className="border-pink-200 dark:border-pink-900 bg-pink-50 dark:bg-pink-950/20">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-pink-600 mt-0.5" />
              <div>
                <p className="font-medium text-pink-900 dark:text-pink-100">Intelligent Sheet Coordination</p>
                <p className="text-sm text-pink-800 dark:text-pink-200 mt-1">
                  The database knows spatial relationships between sheets. Match lines are calculated automatically based on 
                  viewport extents. Renumber a sheet? All cross-references update instantly. Add a detail? The database finds 
                  the perfect spot in the sequence.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-6">
          {/* Sheet List */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Sheet Set</CardTitle>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={updateMatchLines}>
                      <Grid3x3 className="h-4 w-4 mr-2" />
                      Update Match Lines
                    </Button>
                    <Button size="sm" onClick={addSheet} data-testid="button-add-sheet">
                      Add Sheet
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {sheets.map((sheet) => (
                  <Card key={sheet.id} className="hover-elevate">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-bold text-lg font-mono">{sheet.number}</span>
                            <span className="text-sm">{sheet.title}</span>
                            <Badge variant={
                              sheet.status === 'approved' ? 'default' :
                              sheet.status === 'review' ? 'secondary' : 'outline'
                            } className="text-xs">
                              {sheet.status}
                            </Badge>
                          </div>

                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="font-mono">Scale: {sheet.scale}</span>
                            {sheet.matchLines.length > 0 && (
                              <div className="flex items-center gap-1">
                                <Layout className="h-3 w-3" />
                                <span>Match to: {sheet.matchLines.join(', ')}</span>
                              </div>
                            )}
                          </div>

                          {sheet.matchLines.length > 0 && (
                            <div className="mt-2 flex gap-1">
                              {sheet.matchLines.map((dir) => (
                                <Badge key={dir} variant="outline" className="text-xs">
                                  ↔ {dir}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="flex gap-1 ml-4">
                          <Button size="sm" variant="ghost">Edit</Button>
                          <Button size="sm" variant="ghost">Preview</Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Auto-Coordination Rules</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="p-3 border rounded">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Smart Match Line Detection</span>
                    <Badge className="bg-green-600">Active</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Analyzes viewport extents to automatically identify where sheets overlap and places match lines
                  </p>
                </div>

                <div className="p-3 border rounded">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Cross-Reference Updates</span>
                    <Badge className="bg-green-600">Active</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    When you renumber C-3 to C-5, all "See Sheet C-3" notes update automatically across the entire set
                  </p>
                </div>

                <div className="p-3 border rounded">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">Sequence Optimization</span>
                    <Badge className="bg-green-600">Active</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    New detail sheets inserted in logical order based on content similarity and reference frequency
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings & Preview */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Coordination Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Match Line Style</Label>
                  <Select value={matchLineStyle} onValueChange={setMatchLineStyle}>
                    <SelectTrigger data-testid="select-match-line-style">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="circle">Circle with Arrow</SelectItem>
                      <SelectItem value="box">Box with Text</SelectItem>
                      <SelectItem value="cloud">Revision Cloud</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Sheet Numbering</Label>
                  <Select defaultValue="discipline">
                    <SelectTrigger data-testid="select-numbering">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="discipline">By Discipline (C-1, C-2...)</SelectItem>
                      <SelectItem value="sequential">Sequential (1, 2, 3...)</SelectItem>
                      <SelectItem value="custom">Custom Format</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="pt-3 border-t">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm">Auto-Renumber</Label>
                    <Badge variant={autoNumber ? 'default' : 'outline'}>
                      {autoNumber ? 'ON' : 'OFF'}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Automatically update sheet numbers when reordering
                  </p>
                </div>

                <Button variant="outline" className="w-full" size="sm">
                  Configure Title Block
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sheet Layout Visualization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-card border rounded-lg" data-testid="sheet-layout-view">
                  <svg viewBox="0 0 300 300" className="w-full h-full">
                    {/* Sheet C-1 (Overall Site - top left) */}
                    <g>
                      <rect x="20" y="20" width="120" height="80" fill="none" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      <text x="80" y="55" fontSize="14" fontWeight="bold" fill="currentColor" className="text-foreground font-mono" textAnchor="middle">C-1</text>
                      <text x="80" y="70" fontSize="8" fill="currentColor" className="text-muted-foreground" textAnchor="middle">Overall</text>
                      
                      {/* Match lines from C-1 */}
                      {/* East match line to C-2 */}
                      <circle cx="140" cy="60" r="8" fill="none" stroke="hsl(314 100% 40%)" strokeWidth="2" />
                      <text x="140" y="63" fontSize="8" fontWeight="bold" fill="hsl(314 100% 40%)" textAnchor="middle">E</text>
                    </g>

                    {/* Sheet C-2 (North - top right) */}
                    <g>
                      <rect x="160" y="20" width="120" height="80" fill="none" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      <text x="220" y="55" fontSize="14" fontWeight="bold" fill="currentColor" className="text-foreground font-mono" textAnchor="middle">C-2</text>
                      <text x="220" y="70" fontSize="8" fill="currentColor" className="text-muted-foreground" textAnchor="middle">North</text>
                      
                      {/* Match lines from C-2 */}
                      {/* South match line to C-3 */}
                      <circle cx="220" cy="100" r="8" fill="none" stroke="hsl(314 100% 40%)" strokeWidth="2" />
                      <text x="220" y="103" fontSize="8" fontWeight="bold" fill="hsl(314 100% 40%)" textAnchor="middle">S</text>
                    </g>

                    {/* Sheet C-3 (South - bottom right) */}
                    <g>
                      <rect x="160" y="120" width="120" height="80" fill="none" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      <text x="220" y="155" fontSize="14" fontWeight="bold" fill="currentColor" className="text-foreground font-mono" textAnchor="middle">C-3</text>
                      <text x="220" y="170" fontSize="8" fill="currentColor" className="text-muted-foreground" textAnchor="middle">South</text>
                      
                      {/* West match line to C-4 */}
                      <circle cx="160" cy="160" r="8" fill="none" stroke="hsl(314 100% 40%)" strokeWidth="2" />
                      <text x="160" y="163" fontSize="8" fontWeight="bold" fill="hsl(314 100% 40%)" textAnchor="middle">W</text>
                    </g>

                    {/* Sheet C-4 (Utility - bottom left) */}
                    <g>
                      <rect x="20" y="120" width="120" height="80" fill="none" stroke="currentColor" strokeWidth="2" className="text-foreground" />
                      <text x="80" y="155" fontSize="14" fontWeight="bold" fill="currentColor" className="text-foreground font-mono" textAnchor="middle">C-4</text>
                      <text x="80" y="170" fontSize="8" fill="currentColor" className="text-muted-foreground" textAnchor="middle">Utility</text>
                    </g>

                    {/* Sheet C-5 (Profile - bottom spanning) */}
                    <g>
                      <rect x="20" y="220" width="260" height="60" fill="none" stroke="currentColor" strokeWidth="2" className="text-foreground" strokeDasharray="4,2" />
                      <text x="150" y="245" fontSize="14" fontWeight="bold" fill="currentColor" className="text-foreground font-mono" textAnchor="middle">C-5</text>
                      <text x="150" y="260" fontSize="8" fill="currentColor" className="text-muted-foreground" textAnchor="middle">Storm Profile</text>
                    </g>

                    {/* Match line connectors */}
                    <line x1="148" y1="60" x2="152" y2="60" stroke="hsl(314 100% 40%)" strokeWidth="1" strokeDasharray="2,2" />
                    <line x1="220" y1="108" x2="220" y2="112" stroke="hsl(314 100% 40%)" strokeWidth="1" strokeDasharray="2,2" />
                    <line x1="152" y1="160" x2="148" y2="160" stroke="hsl(314 100% 40%)" strokeWidth="1" strokeDasharray="2,2" />

                    {/* Legend */}
                    <g transform="translate(10, 290)">
                      <circle cx="5" cy="0" r="4" fill="none" stroke="hsl(314 100% 40%)" strokeWidth="1.5" />
                      <text x="12" y="3" fontSize="7" fill="currentColor" className="text-muted-foreground">Match Line</text>
                    </g>
                  </svg>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">
                  {sheets.length} sheets • {sheets.reduce((acc, s) => acc + s.matchLines.length, 0)} match lines
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Export Sheet Set</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full" size="sm" onClick={exportToDXF} data-testid="button-export-dxf">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Index (DXF)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToJSON} data-testid="button-export-json">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Sheet Data (JSON)
                </Button>
                <Button variant="outline" className="w-full" size="sm" onClick={exportToCSV} data-testid="button-export-csv">
                  <FileDown className="h-4 w-4 mr-2" />
                  Export List (CSV)
                </Button>
              </CardContent>
            </Card>

            <Tabs defaultValue="stats">
              <TabsList className="w-full">
                <TabsTrigger value="stats" className="flex-1">Stats</TabsTrigger>
                <TabsTrigger value="refs" className="flex-1">X-Refs</TabsTrigger>
              </TabsList>

              <TabsContent value="stats" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Sheets:</span>
                      <span className="font-medium">{sheets.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Match Lines:</span>
                      <span className="font-medium">{sheets.reduce((acc, s) => acc + s.matchLines.length, 0)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Cross-References:</span>
                      <span className="font-medium">24</span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="refs" className="mt-4">
                <Card>
                  <CardContent className="pt-6 space-y-2 text-xs">
                    <div className="p-2 bg-muted/30 rounded">
                      <span className="font-medium">C-1 → C-2</span>
                      <span className="text-muted-foreground ml-2">(3 refs)</span>
                    </div>
                    <div className="p-2 bg-muted/30 rounded">
                      <span className="font-medium">C-2 → C-5</span>
                      <span className="text-muted-foreground ml-2">(2 refs)</span>
                    </div>
                    <div className="p-2 bg-muted/30 rounded">
                      <span className="font-medium">C-4 → C-1</span>
                      <span className="text-muted-foreground ml-2">(1 ref)</span>
                    </div>
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
