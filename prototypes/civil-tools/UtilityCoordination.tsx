import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Zap, Phone, Mail, AlertCircle, CheckCircle, Plus, X } from 'lucide-react';
import { useState } from 'react';

type Utility = {
  id: string;
  company: string;
  type: string;
  status: string;
  requestDate: string;
  responseDate: string | null;
  conflicts: number;
  contact: string;
};

type Conflict = {
  id: string;
  utility: string;
  location: string;
  issue: string;
  severity: 'High' | 'Medium' | 'Low';
  suggestions: string[];
  resolved: boolean;
};

export default function UtilityCoordination() {
  const [utilities, setUtilities] = useState<Utility[]>([
    {
      id: '1',
      company: 'Dominion Energy',
      type: 'Electric',
      status: 'Response Received',
      requestDate: '2024-09-01',
      responseDate: '2024-09-15',
      conflicts: 1,
      contact: 'John Smith',
    },
    {
      id: '2',
      company: 'Washington Gas',
      type: 'Gas',
      status: 'Pending',
      requestDate: '2024-09-01',
      responseDate: null,
      conflicts: 0,
      contact: 'Jane Doe',
    },
    {
      id: '3',
      company: 'Fairfax Water',
      type: 'Water',
      status: 'Response Received',
      requestDate: '2024-09-01',
      responseDate: '2024-09-10',
      conflicts: 0,
      contact: 'Mike Johnson',
    },
  ]);

  const [conflicts, setConflicts] = useState<Conflict[]>([
    {
      id: 'CONF-001',
      utility: 'Dominion Energy - Overhead Power',
      location: 'Station 8+50',
      issue: 'Proposed storm line conflicts with existing power pole',
      severity: 'High',
      suggestions: ['Relocate storm line 10\' north', 'Lower invert by 2\'', 'Coordinate pole relocation'],
      resolved: false,
    },
  ]);

  const [isUtilityDialogOpen, setIsUtilityDialogOpen] = useState(false);
  const [newUtility, setNewUtility] = useState({ company: '', type: '', contact: '' });

  const toggleUtilityStatus = (id: string) => {
    setUtilities(utilities.map(util => 
      util.id === id 
        ? { 
            ...util, 
            status: util.status === 'Pending' ? 'Response Received' : 'Pending',
            responseDate: util.status === 'Pending' ? new Date().toISOString().split('T')[0] : null
          }
        : util
    ));
  };

  const toggleConflictResolution = (id: string) => {
    setConflicts(conflicts.map(conf =>
      conf.id === id ? { ...conf, resolved: !conf.resolved } : conf
    ));
  };

  const removeConflict = (id: string) => {
    setConflicts(conflicts.filter(c => c.id !== id));
  };

  const addUtility = () => {
    if (newUtility.company && newUtility.type) {
      const utility: Utility = {
        id: Date.now().toString(),
        company: newUtility.company,
        type: newUtility.type,
        status: 'Pending',
        requestDate: new Date().toISOString().split('T')[0],
        responseDate: null,
        conflicts: 0,
        contact: newUtility.contact,
      };
      setUtilities([...utilities, utility]);
      setNewUtility({ company: '', type: '', contact: '' });
      setIsUtilityDialogOpen(false);
    }
  };

  const responsesReceived = utilities.filter(u => u.status === 'Response Received').length;
  const pending = utilities.filter(u => u.status === 'Pending').length;
  const activeConflicts = conflicts.filter(c => !c.resolved).length;

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Zap className="h-8 w-8 text-cyan-600" />
              <h1 className="text-3xl font-bold">Utility Coordination</h1>
            </div>
            <p className="text-muted-foreground mt-1">
              Track requests and manage utility conflicts
            </p>
          </div>
          <Badge variant="outline">Prototype</Badge>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">{utilities.length}</p>
              <p className="text-sm text-muted-foreground">Total Requests</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{responsesReceived}</p>
              <p className="text-sm text-muted-foreground">Responses Received</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{pending}</p>
              <p className="text-sm text-muted-foreground">Pending</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{activeConflicts}</p>
              <p className="text-sm text-muted-foreground">Active Conflicts</p>
            </CardContent>
          </Card>
        </div>

        {/* Conflicts Alert */}
        {conflicts.filter(c => !c.resolved).length > 0 && (
          <Card className="border-red-200 dark:border-red-900">
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <CardTitle className="text-red-600 dark:text-red-400">Active Conflicts</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {conflicts.filter(c => !c.resolved).map((conflict) => (
                <div key={conflict.id} className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-semibold">{conflict.utility}</p>
                      <p className="text-sm text-muted-foreground">{conflict.location}</p>
                      <p className="text-sm mt-2">{conflict.issue}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="destructive">{conflict.severity} Priority</Badge>
                      <Button 
                        variant="ghost" 
                        size="icon"
                        onClick={() => removeConflict(conflict.id)}
                        data-testid={`button-remove-conflict-${conflict.id}`}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="bg-muted/30 p-3 rounded">
                    <p className="text-sm font-medium mb-2">Suggested Solutions:</p>
                    <ul className="space-y-1 text-sm">
                      {conflict.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="flex items-center gap-2">
                          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => toggleConflictResolution(conflict.id)}
                    data-testid={`button-resolve-${conflict.id}`}
                  >
                    Mark as Resolved
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Utility Requests */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Utility Company Requests</CardTitle>
              <Dialog open={isUtilityDialogOpen} onOpenChange={setIsUtilityDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" data-testid="button-add-utility">
                    <Plus className="h-4 w-4 mr-1" />
                    Add Request
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>New Utility Request</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 pt-4">
                    <div className="space-y-2">
                      <Label>Company Name</Label>
                      <Input 
                        value={newUtility.company}
                        onChange={(e) => setNewUtility({...newUtility, company: e.target.value})}
                        placeholder="Utility Company"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Type</Label>
                      <Select value={newUtility.type} onValueChange={(value) => setNewUtility({...newUtility, type: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Electric">Electric</SelectItem>
                          <SelectItem value="Gas">Gas</SelectItem>
                          <SelectItem value="Water">Water</SelectItem>
                          <SelectItem value="Sewer">Sewer</SelectItem>
                          <SelectItem value="Telecom">Telecom</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Contact Person</Label>
                      <Input 
                        value={newUtility.contact}
                        onChange={(e) => setNewUtility({...newUtility, contact: e.target.value})}
                        placeholder="Contact name"
                      />
                    </div>
                    <Button onClick={addUtility} className="w-full">Send Request</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {utilities.map((utility) => (
              <div key={utility.id} className="flex items-center justify-between p-4 border rounded hover-elevate">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold">{utility.company}</h3>
                    <Badge variant="outline">{utility.type}</Badge>
                    <button 
                      onClick={() => toggleUtilityStatus(utility.id)}
                      data-testid={`badge-status-${utility.id}`}
                    >
                      {utility.status === 'Response Received' ? (
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          {utility.status}
                        </Badge>
                      ) : (
                        <Badge variant="secondary">{utility.status}</Badge>
                      )}
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Request Sent</p>
                      <p className="font-medium">{utility.requestDate}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Response Date</p>
                      <p className="font-medium">{utility.responseDate || 'Pending'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Contact</p>
                      <p className="font-medium">{utility.contact}</p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon">
                    <Phone className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Mail className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
