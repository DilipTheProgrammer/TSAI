"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { Activity, Brain, Search, Users, AlertTriangle, CheckCircle, Clock, TrendingUp, FileText } from "lucide-react"

const EXAMPLE_DATA = {
  readmission: {
    patientId: "P123",
    clinicalNotes:
      "The 65-year-old male patient admitted for pneumonia has been treated and is now ready for discharge. No acute complications noted. Monitor for readmission risk.",
  },
  riskTrajectory: [
    "Day 1: Patient admitted with acute heart failure symptoms. Immediate treatment started.",
    "Day 2: Clinical improvements noted, but risk factors remain present.",
    "Day 3: Stable condition; discharge planning initiated.",
  ],
  entities: {
    clinicalText:
      "Patient diagnosed with type 2 diabetes mellitus and hypertension. Prescribed metformin and lisinopril.",
  },
  search: {
    query: "patients with congestive heart failure treated with beta blockers",
  },
  cohort: {
    criteria: "acute kidney injury and sepsis",
    notes: [
      "Patient 1: Developed acute kidney injury secondary to septic shock.",
      "Patient 2: No signs of sepsis, but elevated creatinine.",
      "Patient 3: Diagnosed with sepsis and treated with IV antibiotics.",
    ],
  },
}

export default function ClinicalBERTDashboard() {
  const [activeTab, setActiveTab] = useState("readmission")
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)

  const [formData, setFormData] = useState({
    patientId: "",
    clinicalNotes: "",
    clinicalText: "",
    searchQuery: "",
    similarityThreshold: "",
    cohortCriteria: "",
    startDate: "",
    endDate: "",
  })

  const loadExample = (section: string) => {
    switch (section) {
      case "readmission":
        setFormData((prev) => ({
          ...prev,
          patientId: EXAMPLE_DATA.readmission.patientId,
          clinicalNotes: EXAMPLE_DATA.readmission.clinicalNotes,
        }))
        break
      case "entities":
        setFormData((prev) => ({
          ...prev,
          clinicalText: EXAMPLE_DATA.entities.clinicalText,
        }))
        break
      case "search":
        setFormData((prev) => ({
          ...prev,
          searchQuery: EXAMPLE_DATA.search.query,
          similarityThreshold: "0.8",
        }))
        break
      case "cohort":
        setFormData((prev) => ({
          ...prev,
          cohortCriteria: EXAMPLE_DATA.cohort.criteria,
        }))
        break
    }
  }

  // Mock API call function
  const callAPI = async (endpoint: string, data: any) => {
    setLoading(true)
    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Mock responses based on endpoint
    const mockResponses = {
      readmission: {
        risk_score: 0.73,
        risk_level: "High",
        confidence: 0.89,
        factors: ["Previous readmissions", "Comorbidities", "Length of stay"],
        recommendation: "Consider discharge planning intervention",
      },
      entities: {
        entities: [
          { text: "type 2 diabetes mellitus", label: "CONDITION", confidence: 0.95 },
          { text: "hypertension", label: "CONDITION", confidence: 0.93 },
          { text: "metformin", label: "MEDICATION", confidence: 0.92 },
          { text: "lisinopril", label: "MEDICATION", confidence: 0.9 },
        ],
      },
      search: {
        similar_cases: [
          { patient_id: "P001", similarity: 0.91, diagnosis: "Congestive Heart Failure with Beta Blocker Therapy" },
          { patient_id: "P002", similarity: 0.87, diagnosis: "Heart Failure with Reduced Ejection Fraction" },
          { patient_id: "P003", similarity: 0.84, diagnosis: "Cardiomyopathy on Beta Blocker Treatment" },
        ],
      },
      cohort: {
        cohort_size: 247,
        criteria_match: 0.82,
        demographics: { avg_age: 67, gender_ratio: "52% F, 48% M" },
      },
    }

    setResults(mockResponses[endpoint as keyof typeof mockResponses])
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Brain className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-heading font-bold text-foreground">ClinicalBERT AI Dashboard</h1>
            </div>
            <Badge variant="secondary" className="ml-auto">
              API Status: Connected
            </Badge>
          </div>
          <p className="text-muted-foreground mt-1">Healthcare AI predictions and clinical insights</p>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Activity className="h-8 w-8 text-chart-1" />
                <div>
                  <p className="text-sm text-muted-foreground">Predictions Today</p>
                  <p className="text-2xl font-bold">1,247</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-8 w-8 text-chart-2" />
                <div>
                  <p className="text-sm text-muted-foreground">Accuracy Rate</p>
                  <p className="text-2xl font-bold">94.2%</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-chart-3" />
                <div>
                  <p className="text-sm text-muted-foreground">Active Patients</p>
                  <p className="text-2xl font-bold">8,934</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Clock className="h-8 w-8 text-chart-4" />
                <div>
                  <p className="text-sm text-muted-foreground">Avg Response</p>
                  <p className="text-2xl font-bold">1.2s</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="readmission" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Readmission Risk
            </TabsTrigger>
            <TabsTrigger value="entities" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Entity Extraction
            </TabsTrigger>
            <TabsTrigger value="search" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Case Search
            </TabsTrigger>
            <TabsTrigger value="cohort" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Cohort Analysis
            </TabsTrigger>
          </TabsList>

          {/* Readmission Prediction */}
          <TabsContent value="readmission" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="font-heading">30-Day Readmission Prediction</CardTitle>
                      <CardDescription>Analyze patient data to predict readmission risk</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => loadExample("readmission")}>
                      <FileText className="h-4 w-4 mr-2" />
                      Load Example
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="patient-id">Patient ID</Label>
                    <Input
                      id="patient-id"
                      placeholder="Enter patient ID"
                      value={formData.patientId}
                      onChange={(e) => setFormData((prev) => ({ ...prev, patientId: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="clinical-notes">Clinical Notes</Label>
                    <Textarea
                      id="clinical-notes"
                      placeholder="Enter clinical notes and discharge summary..."
                      rows={6}
                      value={formData.clinicalNotes}
                      onChange={(e) => setFormData((prev) => ({ ...prev, clinicalNotes: e.target.value }))}
                    />
                  </div>
                  <Button onClick={() => callAPI("readmission", {})} disabled={loading} className="w-full">
                    {loading ? "Analyzing..." : "Predict Readmission Risk"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-heading">Prediction Results</CardTitle>
                </CardHeader>
                <CardContent>
                  {results && activeTab === "readmission" ? (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-destructive mb-2">
                          {(results.risk_score * 100).toFixed(1)}%
                        </div>
                        <Badge variant={results.risk_level === "High" ? "destructive" : "secondary"}>
                          {results.risk_level} Risk
                        </Badge>
                      </div>
                      <Separator />
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Confidence Level</p>
                        <Progress value={results.confidence * 100} className="mb-2" />
                        <p className="text-sm">{(results.confidence * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Key Risk Factors</p>
                        <div className="space-y-1">
                          {(results.factors || []).map((factor: string, index: number) => (
                            <Badge key={index} variant="outline" className="mr-2">
                              {factor}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <Alert>
                        <CheckCircle className="h-4 w-4" />
                        <AlertDescription>{results.recommendation}</AlertDescription>
                      </Alert>
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">Run a prediction to see results here</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Entity Extraction */}
          <TabsContent value="entities" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="font-heading">Clinical Entity Extraction</CardTitle>
                      <CardDescription>Extract medical entities from clinical text</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => loadExample("entities")}>
                      <FileText className="h-4 w-4 mr-2" />
                      Load Example
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="clinical-text">Clinical Text</Label>
                    <Textarea
                      id="clinical-text"
                      placeholder="Enter clinical notes, discharge summaries, or medical reports..."
                      rows={8}
                      value={formData.clinicalText}
                      onChange={(e) => setFormData((prev) => ({ ...prev, clinicalText: e.target.value }))}
                    />
                  </div>
                  <Button onClick={() => callAPI("entities", {})} disabled={loading} className="w-full">
                    {loading ? "Extracting..." : "Extract Entities"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-heading">Extracted Entities</CardTitle>
                </CardHeader>
                <CardContent>
                  {results && activeTab === "entities" ? (
                    <div className="space-y-3">
                      {(results.entities || []).map((entity: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <span className="font-medium">{entity.text}</span>
                            <Badge variant="outline" className="ml-2">
                              {entity.label}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">{(entity.confidence * 100).toFixed(1)}%</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">Extract entities to see results here</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Case Search */}
          <TabsContent value="search" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="font-heading">Similar Case Search</CardTitle>
                      <CardDescription>Find similar patient cases using semantic search</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => loadExample("search")}>
                      <FileText className="h-4 w-4 mr-2" />
                      Load Example
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="search-query">Search Query</Label>
                    <Textarea
                      id="search-query"
                      placeholder="Describe patient symptoms, conditions, or case details..."
                      rows={6}
                      value={formData.searchQuery}
                      onChange={(e) => setFormData((prev) => ({ ...prev, searchQuery: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="similarity-threshold">Similarity Threshold</Label>
                    <Input
                      id="similarity-threshold"
                      type="number"
                      placeholder="0.8"
                      min="0"
                      max="1"
                      step="0.1"
                      value={formData.similarityThreshold}
                      onChange={(e) => setFormData((prev) => ({ ...prev, similarityThreshold: e.target.value }))}
                    />
                  </div>
                  <Button onClick={() => callAPI("search", {})} disabled={loading} className="w-full">
                    {loading ? "Searching..." : "Search Similar Cases"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-heading">Similar Cases Found</CardTitle>
                </CardHeader>
                <CardContent>
                  {results && activeTab === "search" ? (
                    <div className="space-y-3">
                      {(results.similar_cases || []).map((case_item: any, index: number) => (
                        <div key={index} className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{case_item.patient_id}</span>
                            <Badge variant="secondary">{(case_item.similarity * 100).toFixed(1)}% match</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{case_item.diagnosis}</p>
                          <Progress value={case_item.similarity * 100} className="mt-2" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">Search for cases to see results here</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Cohort Analysis */}
          <TabsContent value="cohort" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="font-heading">Cohort Identification</CardTitle>
                      <CardDescription>Identify patient cohorts based on clinical criteria</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => loadExample("cohort")}>
                      <FileText className="h-4 w-4 mr-2" />
                      Load Example
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="cohort-criteria">Clinical Criteria</Label>
                    <Textarea
                      id="cohort-criteria"
                      placeholder="Define cohort criteria (e.g., diabetes patients with HbA1c > 7.0, age 50-70)..."
                      rows={4}
                      value={formData.cohortCriteria}
                      onChange={(e) => setFormData((prev) => ({ ...prev, cohortCriteria: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="date-range">Date Range</Label>
                    <div className="grid grid-cols-2 gap-2">
                      <Input
                        type="date"
                        placeholder="Start date"
                        value={formData.startDate}
                        onChange={(e) => setFormData((prev) => ({ ...prev, startDate: e.target.value }))}
                      />
                      <Input
                        type="date"
                        placeholder="End date"
                        value={formData.endDate}
                        onChange={(e) => setFormData((prev) => ({ ...prev, endDate: e.target.value }))}
                      />
                    </div>
                  </div>
                  <Button onClick={() => callAPI("cohort", {})} disabled={loading} className="w-full">
                    {loading ? "Analyzing..." : "Identify Cohort"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-heading">Cohort Analysis Results</CardTitle>
                </CardHeader>
                <CardContent>
                  {results && activeTab === "cohort" ? (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-primary mb-2">{results.cohort_size}</div>
                        <p className="text-muted-foreground">Patients identified</p>
                      </div>
                      <Separator />
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Criteria Match Rate</p>
                        <Progress value={results.criteria_match * 100} className="mb-2" />
                        <p className="text-sm">{(results.criteria_match * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">Demographics</p>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Average Age:</span>
                            <span className="font-medium">{results.demographics?.avg_age || "N/A"} years</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Gender Distribution:</span>
                            <span className="font-medium">{results.demographics?.gender_ratio || "N/A"}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      Run cohort analysis to see results here
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
