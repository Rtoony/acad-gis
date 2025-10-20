import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import ToolGallery from "@/pages/ToolGallery";
import PipeNetworkEditor from "@/pages/Home";
import AlignmentEditor from "@/pages/AlignmentEditor";
import Examples from "@/pages/Examples";
import NotFound from "@/pages/not-found";

// Example components - Pipe Network
import ThemeToggleExample from "@/components/examples/ThemeToggle";
import ExportControlsExample from "@/components/examples/ExportControls";
import NetworkDiagramExample from "@/components/examples/NetworkDiagram";
import ProjectInfoExample from "@/components/examples/ProjectInfo";
import ValidationSummaryExample from "@/components/examples/ValidationSummary";
import PipeTableExample from "@/components/examples/PipeTable";
import ProjectSelectorExample from "@/components/examples/ProjectSelector";
import CompositeWorkflowExample from "@/components/examples/CompositeWorkflow";
import EdgeCasesExample from "@/components/examples/EdgeCases";

// Example components - Civil Engineering Tools
import SheetNoteManagerExample from "@/components/examples/SheetNoteManager";
import SheetSetManagerExample from "@/components/examples/SheetSetManager";
import LegendManagerExample from "@/components/examples/LegendManager";
import TaskManagerExample from "@/components/examples/TaskManager";
import LayerManagerExample from "@/components/examples/LayerManager";
import AlignmentEditorExample from "@/components/examples/AlignmentEditor";

// Tool Pages
import CrossSectionBuilder from "@/pages/tools/CrossSectionBuilder";
import GradingCalculator from "@/pages/tools/GradingCalculator";
import BMPManager from "@/pages/tools/BMPManager";
import UtilityCoordination from "@/pages/tools/UtilityCoordination";
import ErosionControl from "@/pages/tools/ErosionControl";
import PlanReviewTracker from "@/pages/tools/PlanReviewTracker";
import QuantityTakeoff from "@/pages/tools/QuantityTakeoff";
import PermitWizard from "@/pages/tools/PermitWizard";
import MOTPlan from "@/pages/tools/MOTPlan";
import AsBuiltManager from "@/pages/tools/AsBuiltManager";
import SurveyStakeout from "@/pages/tools/SurveyStakeout";
import Photolog from "@/pages/tools/Photolog";

// Intelligence Layer (Paradigm Shift) Tools
import ViewAssembler from "@/pages/tools/ViewAssembler";
import PlotProfileManager from "@/pages/tools/PlotProfileManager";
import LiveComplianceDashboard from "@/pages/tools/LiveComplianceDashboard";
import ConstraintSolver from "@/pages/tools/ConstraintSolver";
import LivePlanProfileSync from "@/pages/tools/LivePlanProfileSync";
import SheetSetCoordinator from "@/pages/tools/SheetSetCoordinator";
import RevisionIntelligence from "@/pages/tools/RevisionIntelligence";
import ClashDetection from "@/pages/tools/ClashDetection";

function Router() {
  return (
    <Switch>
      <Route path="/" component={ToolGallery} />
      <Route path="/pipe-network" component={PipeNetworkEditor} />
      <Route path="/alignment-editor" component={AlignmentEditor} />
      <Route path="/examples" component={Examples} />
      
      {/* Example Routes */}
      <Route path="/examples/theme-toggle" component={ThemeToggleExample} />
      <Route path="/examples/export-controls" component={ExportControlsExample} />
      <Route path="/examples/network-diagram" component={NetworkDiagramExample} />
      <Route path="/examples/project-info" component={ProjectInfoExample} />
      <Route path="/examples/validation-summary" component={ValidationSummaryExample} />
      <Route path="/examples/pipe-table" component={PipeTableExample} />
      <Route path="/examples/project-selector" component={ProjectSelectorExample} />
      <Route path="/examples/composite-workflow" component={CompositeWorkflowExample} />
      <Route path="/examples/edge-cases" component={EdgeCasesExample} />
      
      {/* Civil Engineering Tool Examples */}
      <Route path="/examples/sheet-note-manager" component={SheetNoteManagerExample} />
      <Route path="/examples/sheet-set-manager" component={SheetSetManagerExample} />
      <Route path="/examples/legend-manager" component={LegendManagerExample} />
      <Route path="/examples/task-manager" component={TaskManagerExample} />
      <Route path="/examples/layer-manager" component={LayerManagerExample} />
      <Route path="/examples/alignment-editor" component={AlignmentEditorExample} />
      
      {/* Tool Routes - Intelligence Layer (Paradigm Shift) */}
      <Route path="/tools/view-assembler" component={ViewAssembler} />
      <Route path="/tools/plot-profile-manager" component={PlotProfileManager} />
      <Route path="/tools/live-compliance-dashboard" component={LiveComplianceDashboard} />
      <Route path="/tools/constraint-solver" component={ConstraintSolver} />
      <Route path="/tools/live-plan-profile-sync" component={LivePlanProfileSync} />
      <Route path="/tools/sheet-set-coordinator" component={SheetSetCoordinator} />
      <Route path="/tools/revision-intelligence" component={RevisionIntelligence} />
      <Route path="/tools/clash-detection" component={ClashDetection} />
      
      {/* Tool Routes - Design & Layout */}
      <Route path="/tools/cross-section-builder" component={CrossSectionBuilder} />
      <Route path="/tools/grading-calculator" component={GradingCalculator} />
      
      {/* Tool Routes - Stormwater & Utilities */}
      <Route path="/tools/bmp-manager" component={BMPManager} />
      <Route path="/tools/utility-coordination" component={UtilityCoordination} />
      <Route path="/tools/erosion-control" component={ErosionControl} />
      
      {/* Tool Routes - Project Coordination */}
      <Route path="/tools/plan-review-tracker" component={PlanReviewTracker} />
      <Route path="/tools/quantity-takeoff" component={QuantityTakeoff} />
      <Route path="/tools/permit-wizard" component={PermitWizard} />
      
      {/* Tool Routes - Construction Support */}
      <Route path="/tools/mot-planner" component={MOTPlan} />
      <Route path="/tools/as-built-manager" component={AsBuiltManager} />
      <Route path="/tools/survey-stakeout" component={SurveyStakeout} />
      <Route path="/tools/photolog" component={Photolog} />
      
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
