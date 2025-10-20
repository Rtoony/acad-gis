import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useState } from 'react';
import { Layers, Plus, Trash2, CheckCircle, AlertCircle } from 'lucide-react';

type Transition = {
  id: string;
  startStation: string;
  endStation: string;
  description: string;
};

export default function CrossSectionBuilder() {
  const [laneWidth, setLaneWidth] = useState([12]);
  const [shoulderWidth, setShoulderWidth] = useState([8]);
  const [slope, setSlope] = useState([2]);
  const [transitions, setTransitions] = useState<Transition[]>([
    { id: '1', startStation: '0+00', endStation: '12+50', description: '2-lane local road' },
    { id: '2', startStation: '12+50', endStation: '15+00', description: 'Transition to 4-lane' },
    { id: '3', startStation: '15+00', endStation: '25+00', description: '4-lane collector' },
  ]);
  const [newTransition, setNewTransition] = useState({ startStation: '', endStation: '', description: '' });
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const totalWidth = (laneWidth[0] * 2) + (shoulderWidth[0] * 2);
  const isStandardCompliant = laneWidth[0] >= 11 && shoulderWidth[0] >= 4;

  const applyTemplate = (template: string) => {
    switch (template) {
      case 'local':
        setLaneWidth([11]);
        setShoulderWidth([0]);
        setSlope([2]);
        break;
      case 'collector':
        setLaneWidth([12]);
        setShoulderWidth([4]);
        setSlope([2]);
        break;
      case 'arterial':
        setLaneWidth([12]);
        setShoulderWidth([10]);
        setSlope([2]);
        break;
    }
  };

  const addTransition = () => {
    if (newTransition.startStation && newTransition.endStation) {
      setTransitions([...transitions, { ...newTransition, id: Date.now().toString() }]);
      setNewTransition({ startStation: '', endStation: '', description: '' });
      setIsDialogOpen(false);
    }
  };

  const removeTransition = (id: string) => {
    setTransitions(transitions.filter(t => t.id !== id));
  };

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Layers className="h-8 w-8 text-blue-600" />
              <h1 className="text-3xl font-bold">Cross-Section Builder</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Parametric typical sections with auto-transitions
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Controls */}
          <div className="col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Section Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Lane Width: {laneWidth[0]} ft</Label>
                  <Slider
                    value={laneWidth}
                    onValueChange={setLaneWidth}
                    min={10}
                    max={14}
                    step={1}
                    data-testid="slider-lane-width"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Shoulder Width: {shoulderWidth[0]} ft</Label>
                  <Slider
                    value={shoulderWidth}
                    onValueChange={setShoulderWidth}
                    min={0}
                    max={12}
                    step={1}
                    data-testid="slider-shoulder-width"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Cross Slope: {slope[0]}%</Label>
                  <Slider
                    value={slope}
                    onValueChange={setSlope}
                    min={1}
                    max={4}
                    step={0.5}
                    data-testid="slider-cross-slope"
                  />
                </div>

                <div className="pt-4 border-t">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Width:</span>
                      <span className="font-mono font-medium">{totalWidth} ft</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Travel Lanes:</span>
                      <span className="font-mono font-medium">2 × {laneWidth[0]} ft</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Shoulders:</span>
                      <span className="font-mono font-medium">2 × {shoulderWidth[0] || 'None'} ft</span>
                    </div>
                  </div>
                </div>

                {/* Live Validation */}
                <div className="pt-4 border-t">
                  {isStandardCompliant ? (
                    <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                      <CheckCircle className="h-4 w-4" />
                      <span>Meets standard requirements</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                      <AlertCircle className="h-4 w-4" />
                      <span>Below typical standards (Lane ≥11', Shoulder ≥4')</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Templates</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover-elevate" 
                  onClick={() => applyTemplate('local')}
                  data-testid="button-template-local"
                >
                  Local Road (22' typical)
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover-elevate" 
                  onClick={() => applyTemplate('collector')}
                  data-testid="button-template-collector"
                >
                  Collector (32' typical)
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover-elevate" 
                  onClick={() => applyTemplate('arterial')}
                  data-testid="button-template-arterial"
                >
                  Arterial (44' typical)
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Visual Preview */}
          <div className="col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Section Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-muted/30 rounded-lg p-8">
                  {/* Simple cross-section visual */}
                  <svg viewBox="0 0 400 200" className="w-full h-64">
                    {/* Ground line */}
                    <line x1="0" y1="100" x2="400" y2="100" stroke="currentColor" strokeWidth="1" className="text-muted-foreground" />
                    
                    {/* Left shoulder */}
                    {shoulderWidth[0] > 0 && (
                      <polygon
                        points={`0,100 ${50 + shoulderWidth[0] * 3},${100 - slope[0] * 2} ${50 + shoulderWidth[0] * 3},100`}
                        fill="currentColor"
                        className="text-yellow-600/30"
                      />
                    )}
                    
                    {/* Left lane */}
                    <polygon
                      points={`${50 + shoulderWidth[0] * 3},${100 - slope[0] * 2} ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 3},${100 - slope[0] * 3} ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 3},100 ${50 + shoulderWidth[0] * 3},100`}
                      fill="currentColor"
                      className="text-gray-600/50"
                    />
                    
                    {/* Right lane */}
                    <polygon
                      points={`${50 + shoulderWidth[0] * 3 + laneWidth[0] * 3},${100 - slope[0] * 3} ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 6},${100 - slope[0] * 2} ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 6},100 ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 3},100`}
                      fill="currentColor"
                      className="text-gray-600/50"
                    />
                    
                    {/* Right shoulder */}
                    {shoulderWidth[0] > 0 && (
                      <polygon
                        points={`${50 + shoulderWidth[0] * 3 + laneWidth[0] * 6},${100 - slope[0] * 2} ${50 + shoulderWidth[0] * 6 + laneWidth[0] * 6},100 ${50 + shoulderWidth[0] * 3 + laneWidth[0] * 6},100`}
                        fill="currentColor"
                        className="text-yellow-600/30"
                      />
                    )}
                    
                    {/* Center line */}
                    <line 
                      x1={50 + shoulderWidth[0] * 3 + laneWidth[0] * 3} 
                      y1={100 - slope[0] * 3} 
                      x2={50 + shoulderWidth[0] * 3 + laneWidth[0] * 3} 
                      y2="100" 
                      stroke="yellow" 
                      strokeWidth="2" 
                      strokeDasharray="5,5" 
                    />
                    
                    {/* Dimension lines */}
                    <text x="200" y="30" textAnchor="middle" className="text-xs fill-current">
                      {totalWidth}' Total Width
                    </text>
                  </svg>

                  <div className="flex justify-around mt-4 text-xs text-muted-foreground">
                    {shoulderWidth[0] > 0 && <span>Shoulder</span>}
                    <span>Lane</span>
                    <span>Lane</span>
                    {shoulderWidth[0] > 0 && <span>Shoulder</span>}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="stations">
              <TabsList className="w-full">
                <TabsTrigger value="stations" className="flex-1">Station Transitions</TabsTrigger>
                <TabsTrigger value="layers" className="flex-1">Layer Codes</TabsTrigger>
              </TabsList>
              <TabsContent value="stations">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">Transitions</CardTitle>
                      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                          <Button size="sm" data-testid="button-add-transition">
                            <Plus className="h-4 w-4 mr-1" />
                            Add
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Add Station Transition</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4 pt-4">
                            <div className="space-y-2">
                              <Label>Start Station</Label>
                              <Input 
                                value={newTransition.startStation}
                                onChange={(e) => setNewTransition({...newTransition, startStation: e.target.value})}
                                placeholder="0+00"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label>End Station</Label>
                              <Input 
                                value={newTransition.endStation}
                                onChange={(e) => setNewTransition({...newTransition, endStation: e.target.value})}
                                placeholder="10+00"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label>Description</Label>
                              <Input 
                                value={newTransition.description}
                                onChange={(e) => setNewTransition({...newTransition, description: e.target.value})}
                                placeholder="Section description"
                              />
                            </div>
                            <Button onClick={addTransition} className="w-full">Add Transition</Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {transitions.map((transition, idx) => (
                        <div key={transition.id} className="flex items-center justify-between p-3 border rounded hover-elevate">
                          <div>
                            <p className="font-medium">Sta {transition.startStation} to {transition.endStation}</p>
                            <p className="text-sm text-muted-foreground">{transition.description}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            {idx === 0 && <Badge variant="outline">Current</Badge>}
                            <Button 
                              variant="ghost" 
                              size="icon"
                              onClick={() => removeTransition(transition.id)}
                              data-testid={`button-remove-transition-${transition.id}`}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="layers">
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-2 font-mono text-sm">
                      <div className="flex justify-between p-2 bg-muted/30 rounded">
                        <span>C-ROAD-PVMT</span>
                        <span className="text-muted-foreground">Pavement surface</span>
                      </div>
                      <div className="flex justify-between p-2 bg-muted/30 rounded">
                        <span>C-ROAD-STRP</span>
                        <span className="text-muted-foreground">Striping</span>
                      </div>
                      <div className="flex justify-between p-2 bg-muted/30 rounded">
                        <span>C-ROAD-SHLD</span>
                        <span className="text-muted-foreground">Shoulders</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button data-testid="button-apply-section">Apply to Alignment</Button>
          <Button variant="outline" data-testid="button-save-section">Save Section</Button>
        </div>
      </div>
    </div>
  );
}
