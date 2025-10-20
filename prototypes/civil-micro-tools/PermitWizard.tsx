import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { FileCheck, CheckCircle, Circle, AlertCircle } from 'lucide-react';

export default function PermitWizard() {
  const requirements = [
    { item: 'Site Plan (24" x 36")', status: 'complete', auto: true },
    { item: 'Grading Plan', status: 'complete', auto: true },
    { item: 'Stormwater Management Plan', status: 'complete', auto: true },
    { item: 'Erosion Control Plan', status: 'complete', auto: true },
    { item: 'Stormwater Calculations', status: 'complete', auto: true },
    { item: 'Erosion Control Bond Calculation', status: 'pending', auto: true },
    { item: 'Stormwater Narrative', status: 'pending', auto: false },
    { item: 'Professional Engineer Seal', status: 'required', auto: false },
  ];

  const completed = requirements.filter((r) => r.status === 'complete').length;
  const progress = (completed / requirements.length) * 100;

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <FileCheck className="h-8 w-8 text-orange-600" />
              <h1 className="text-3xl font-bold">Permit Application Wizard</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Jurisdiction-specific permit applications
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        {/* Progress */}
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="font-medium">Application Progress</span>
                <span className="text-muted-foreground">{completed} of {requirements.length} items</span>
              </div>
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {requirements.length - completed} items remaining for submission
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Jurisdiction */}
        <Card>
          <CardHeader>
            <CardTitle>Permit Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Jurisdiction</p>
                <p className="font-medium">Fairfax County, Virginia</p>
              </div>
              <div>
                <p className="text-muted-foreground">Permit Type</p>
                <p className="font-medium">Site Development Plan</p>
              </div>
              <div>
                <p className="text-muted-foreground">Review Fee</p>
                <p className="font-medium">$3,450 (auto-calculated)</p>
              </div>
              <div>
                <p className="text-muted-foreground">Estimated Review Time</p>
                <p className="font-medium">45-60 business days</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Requirements Checklist */}
        <Card>
          <CardHeader>
            <CardTitle>Submittal Requirements</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {requirements.map((req, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  {req.status === 'complete' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : req.status === 'pending' ? (
                    <Circle className="h-5 w-5 text-blue-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                  )}
                  <div>
                    <p className="font-medium">{req.item}</p>
                    {req.auto && (
                      <p className="text-xs text-muted-foreground">Auto-generated from project data</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {req.status === 'complete' ? (
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                      Ready
                    </Badge>
                  ) : req.status === 'pending' ? (
                    <Badge variant="secondary">Generating...</Badge>
                  ) : (
                    <Badge variant="outline">Action Required</Badge>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="space-y-3">
          <Button className="w-full" size="lg" disabled={progress < 100} data-testid="button-submit">
            <FileCheck className="h-4 w-4 mr-2" />
            Generate Submittal Package
          </Button>
          <p className="text-sm text-muted-foreground text-center">
            All auto-generated items will be compiled with proper formatting and transmittal letter
          </p>
        </div>
      </div>
    </div>
  );
}
