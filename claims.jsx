import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

export default function ClaimPredictor() {
  const [formData, setFormData] = useState({
    PatientAge: '',
    PatientIncome: '',
    ClaimType: '',
    EmploymentStatus: '',
    ClaimDate: '',
    ClaimAmount: ''
  });

  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPrediction(null);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/predict/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok) {
        setPrediction(data.prediction);
      } else {
        setError(data.detail || "Prediction failed.");
      }
    } catch (err) {
      setError("Server error. Check your FastAPI backend.");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10">
      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-bold mb-4">Insurance Claim Predictor</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {["PatientAge", "PatientIncome", "ClaimAmount"].map(field => (
              <div key={field}>
                <Label htmlFor={field}>{field}</Label>
                <Input
                  id={field}
                  name={field}
                  type="number"
                  value={formData[field]}
                  onChange={handleChange}
                  required
                />
              </div>
            ))}
            <div>
              <Label htmlFor="ClaimType">Claim Type</Label>
              <Input
                id="ClaimType"
                name="ClaimType"
                type="text"
                value={formData.ClaimType}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <Label htmlFor="EmploymentStatus">Employment Status</Label>
              <Input
                id="EmploymentStatus"
                name="EmploymentStatus"
                type="text"
                value={formData.EmploymentStatus}
                onChange={handleChange}
                required
              />
            </div>
            <div>
              <Label htmlFor="ClaimDate">Claim Date</Label>
              <Input
                id="ClaimDate"
                name="ClaimDate"
                type="date"
                value={formData.ClaimDate}
                onChange={handleChange}
                required
              />
            </div>
            <Button type="submit" className="w-full">Predict</Button>
          </form>
          {prediction !== null && (
            <div className="mt-4 text-green-700 font-medium">
              Predicted Claim Outcome: <strong>{prediction.toFixed(2)}</strong>
            </div>
          )}
          {error && (
            <div className="mt-4 text-red-600">
              Error: {error}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
