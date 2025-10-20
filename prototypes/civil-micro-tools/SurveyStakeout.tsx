import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { MapPin, Download } from 'lucide-react';

export default function SurveyStakeout() {
  const pointTypes = [
    { type: 'Curb Returns', count: 24, selected: true },
    { type: 'Manhole Centers', count: 8, selected: true },
    { type: 'Property Corners', count: 6, selected: false },
    { type: 'Building Corners', count: 4, selected: true },
    { type: 'Inlet Locations', count: 12, selected: true },
    { type: 'Light Pole Bases', count: 18, selected: false },
  ];

  const selectedCount = pointTypes.filter((p) => p.selected).length;
  const totalPoints = pointTypes.filter((p) => p.selected).reduce((sum, p) => sum + p.count, 0);

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <MapPin className="h-8 w-8 text-yellow-600" />
              <h1 className="text-3xl font-bold">Survey Stakeout Generator</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Export points for field GPS equipment
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">{selectedCount}</p>
              <p className="text-sm text-muted-foreground">Point Categories</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">{totalPoints}</p>
              <p className="text-sm text-muted-foreground">Total Points</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">State Plane</p>
              <p className="text-sm text-muted-foreground">Coordinate System</p>
            </CardContent>
          </Card>
        </div>

        {/* Point Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Point Types</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {pointTypes.map((point) => (
              <div key={point.type} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <Checkbox checked={point.selected} />
                  <div>
                    <p className="font-medium">{point.type}</p>
                    <p className="text-sm text-muted-foreground">{point.count} points from design</p>
                  </div>
                </div>
                <Badge variant="outline">{point.count}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Export Formats */}
        <Card>
          <CardHeader>
            <CardTitle>Export Format</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-3 gap-3">
              <Button variant="outline" className="justify-start" data-testid="button-export-csv">
                <Download className="h-4 w-4 mr-2" />
                CSV (Generic)
              </Button>
              <Button variant="outline" className="justify-start" data-testid="button-export-trimble">
                <Download className="h-4 w-4 mr-2" />
                Trimble DC File
              </Button>
              <Button variant="outline" className="justify-start" data-testid="button-export-leica">
                <Download className="h-4 w-4 mr-2" />
                Leica GSI
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Points include: ID, Northing, Easting, Elevation, Description
            </p>
          </CardContent>
        </Card>

        {/* Preview */}
        <Card>
          <CardHeader>
            <CardTitle>Point Preview (first 5)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-sm space-y-1 bg-muted/30 p-4 rounded">
              <div className="text-muted-foreground">ID, N, E, Elev, Desc</div>
              <div>CR-1, 2245678.45, 11876543.21, 102.35, Curb Return NE</div>
              <div>CR-2, 2245690.12, 11876555.87, 102.18, Curb Return SE</div>
              <div>MH-1, 2245701.33, 11876498.45, 100.50, Manhole Center</div>
              <div>MH-2, 2245720.88, 11876520.12, 100.72, Manhole Center</div>
              <div>BLDG-1, 2245650.25, 11876580.90, 105.00, Building Corner NW</div>
            </div>
          </CardContent>
        </Card>

        <Button className="w-full" size="lg" data-testid="button-export-stakeout">
          <Download className="h-4 w-4 mr-2" />
          Export Stakeout Points ({totalPoints} points)
        </Button>
      </div>
    </div>
  );
}
