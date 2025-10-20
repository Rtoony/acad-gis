import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Droplet, Calendar, CheckCircle, AlertTriangle, Plus, Search, Trash2, ArrowLeft } from 'lucide-react';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { queryClient, apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'wouter';
import type { BMP } from '@shared/schema';

export default function BMPManager() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newBMP, setNewBMP] = useState({
    bmpId: '',
    type: '',
    area: '',
    drainageArea: '',
    installDate: '',
  });

  // Fetch all BMPs
  const { data: bmps, isLoading } = useQuery<BMP[]>({
    queryKey: ['/api/bmps'],
  });

  // Create BMP mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      return apiRequest('POST', '/api/bmps', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bmps'] });
      toast({ title: 'BMP created successfully' });
      setIsDialogOpen(false);
      setNewBMP({ bmpId: '', type: '', area: '', drainageArea: '', installDate: '' });
    },
    onError: () => {
      toast({ title: 'Failed to create BMP', variant: 'destructive' });
    },
  });

  // Delete BMP mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      return apiRequest('DELETE', `/api/bmps/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bmps'] });
      toast({ title: 'BMP deleted successfully' });
    },
    onError: () => {
      toast({ title: 'Failed to delete BMP', variant: 'destructive' });
    },
  });

  // Update BMP mutation (toggle compliance)
  const updateMutation = useMutation({
    mutationFn: async ({ id, compliance }: { id: number; compliance: string }) => {
      return apiRequest('PUT', `/api/bmps/${id}`, { compliance });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/bmps'] });
    },
    onError: () => {
      toast({ title: 'Failed to update BMP', variant: 'destructive' });
    },
  });

  const filteredBMPs = (bmps || []).filter(bmp => {
    const matchesSearch = bmp.bmpId.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         bmp.type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || bmp.type === filterType;
    return matchesSearch && matchesType;
  });

  const totalAcres = (bmps || []).reduce((sum, bmp) => sum + bmp.drainageArea, 0);
  const compliantCount = (bmps || []).filter(bmp => bmp.compliance === 'Good').length;
  const needsAttentionCount = (bmps || []).filter(bmp => bmp.compliance === 'Needs Attention').length;

  const addBMP = () => {
    if (newBMP.bmpId && newBMP.type) {
      const bmpData = {
        bmpId: newBMP.bmpId,
        type: newBMP.type,
        area: parseFloat(newBMP.area) || 0,
        drainageArea: parseFloat(newBMP.drainageArea) || 0,
        status: 'Active',
        installDate: newBMP.installDate || new Date().toISOString().split('T')[0],
        compliance: 'Good',
      };
      createMutation.mutate(bmpData);
    }
  };

  const toggleCompliance = (bmp: BMP) => {
    const newCompliance = bmp.compliance === 'Good' ? 'Needs Attention' : 'Good';
    updateMutation.mutate({ id: bmp.id, compliance: newCompliance });
  };

  if (isLoading) {
    return (
      <div className="p-6 bg-background min-h-screen">
        <div className="max-w-7xl mx-auto">
          <p className="text-muted-foreground">Loading BMPs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-background min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/">
              <Button variant="ghost" size="icon" data-testid="button-back">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <Droplet className="h-8 w-8 text-cyan-600" />
            <div>
              <h1 className="text-3xl font-bold">BMP Manager</h1>
              <p className="text-muted-foreground mt-1">
                Lifecycle management for stormwater BMPs
              </p>
            </div>
          </div>
          <Badge>Production</Badge>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">{bmps?.length || 0}</p>
              <p className="text-sm text-muted-foreground">Active BMPs</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold">{totalAcres.toFixed(1)}</p>
              <p className="text-sm text-muted-foreground">Total Acres Treated</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{compliantCount}</p>
              <p className="text-sm text-muted-foreground">Compliant</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{needsAttentionCount}</p>
              <p className="text-sm text-muted-foreground">Needs Attention</p>
            </CardContent>
          </Card>
        </div>

        {/* BMP List */}
        <Tabs defaultValue="active">
          <TabsList>
            <TabsTrigger value="active">Active BMPs</TabsTrigger>
            <TabsTrigger value="maintenance">Maintenance Schedule</TabsTrigger>
            <TabsTrigger value="reports">Compliance Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="space-y-3 mt-4">
            {/* Search and Filter */}
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search BMPs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                  data-testid="input-search-bmp"
                />
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-48" data-testid="select-bmp-type">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="Bioretention">Bioretention</SelectItem>
                  <SelectItem value="Dry Pond">Dry Pond</SelectItem>
                  <SelectItem value="Permeable Pavement">Permeable Pavement</SelectItem>
                  <SelectItem value="Wet Pond">Wet Pond</SelectItem>
                </SelectContent>
              </Select>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="button-add-bmp">
                    <Plus className="h-4 w-4 mr-1" />
                    Add BMP
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New BMP</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 pt-4">
                    <div className="space-y-2">
                      <Label>BMP ID</Label>
                      <Input 
                        value={newBMP.bmpId}
                        onChange={(e) => setNewBMP({...newBMP, bmpId: e.target.value})}
                        placeholder="BMP-04"
                        data-testid="input-bmp-id"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Type</Label>
                      <Select value={newBMP.type} onValueChange={(value) => setNewBMP({...newBMP, type: value})}>
                        <SelectTrigger data-testid="select-bmp-type-dialog">
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Bioretention">Bioretention</SelectItem>
                          <SelectItem value="Dry Pond">Dry Pond</SelectItem>
                          <SelectItem value="Wet Pond">Wet Pond</SelectItem>
                          <SelectItem value="Permeable Pavement">Permeable Pavement</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <Label>BMP Area (sq ft)</Label>
                        <Input 
                          type="number"
                          value={newBMP.area}
                          onChange={(e) => setNewBMP({...newBMP, area: e.target.value})}
                          placeholder="1000"
                          data-testid="input-area"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Drainage Area (acres)</Label>
                        <Input 
                          type="number"
                          value={newBMP.drainageArea}
                          onChange={(e) => setNewBMP({...newBMP, drainageArea: e.target.value})}
                          placeholder="2.5"
                          data-testid="input-drainage-area"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Install Date</Label>
                      <Input 
                        type="date"
                        value={newBMP.installDate}
                        onChange={(e) => setNewBMP({...newBMP, installDate: e.target.value})}
                        data-testid="input-install-date"
                      />
                    </div>
                    <Button
                      onClick={addBMP}
                      className="w-full"
                      disabled={!newBMP.bmpId || !newBMP.type || createMutation.isPending}
                      data-testid="button-save-bmp"
                    >
                      {createMutation.isPending ? 'Adding...' : 'Add BMP'}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* BMP Cards */}
            <div className="space-y-3">
              {filteredBMPs.length > 0 ? (
                filteredBMPs.map((bmp) => (
                  <Card key={bmp.id} className="hover-elevate">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold">{bmp.bmpId}</h3>
                            <Badge variant="outline">{bmp.type}</Badge>
                            <button
                              onClick={() => toggleCompliance(bmp)}
                              className="cursor-pointer"
                              data-testid={`badge-compliance-${bmp.bmpId}`}
                            >
                              {bmp.compliance === 'Good' ? (
                                <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Compliant
                                </Badge>
                              ) : (
                                <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
                                  <AlertTriangle className="h-3 w-3 mr-1" />
                                  Needs Attention
                                </Badge>
                              )}
                            </button>
                          </div>
                          <div className="grid grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="text-muted-foreground">BMP Area</p>
                              <p className="font-medium">{bmp.area} sq ft</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Drainage Area</p>
                              <p className="font-medium">{bmp.drainageArea} acres</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Status</p>
                              <p className="font-medium">{bmp.status}</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Install Date</p>
                              <p className="font-medium">{bmp.installDate || 'N/A'}</p>
                            </div>
                          </div>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => {
                            if (confirm('Are you sure you want to delete this BMP?')) {
                              deleteMutation.mutate(bmp.id);
                            }
                          }}
                          data-testid={`button-remove-${bmp.bmpId}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="pt-6 text-center text-muted-foreground">
                    {searchQuery || filterType !== 'all' 
                      ? 'No BMPs found matching your search' 
                      : 'No BMPs yet. Create your first BMP to get started.'}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="maintenance" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Maintenance Tasks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Maintenance scheduling will be available in a future update. Add inspections and maintenance records to track BMP lifecycle.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Annual Compliance Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <Button className="w-full" data-testid="button-generate-report" disabled>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Generate Annual Report
                </Button>
                <p className="text-sm text-muted-foreground mt-4">
                  Auto-generates report from last 12 months of inspection data, photos, and maintenance records (Coming soon)
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
