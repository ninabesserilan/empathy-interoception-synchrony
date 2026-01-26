// Save this as test_curve_interpolator.js
// Run with: node test_curve_interpolator.js
// Make sure curve-interpolator is installed: npm install curve-interpolator

const CurveInterpolator = require('curve-interpolator').CurveInterpolator;

// Test case: Simple IBI-like data
const testPoints = [
    [0, 520],
    [1, 505],
    [2, 515],
    [5, 510],  // Gap of 3 indices (3, 4 missing)
    [6, 500],
    [7, 495]
];

console.log('Input points:');
console.log(JSON.stringify(testPoints, null, 2));

// Create interpolator with tension 0.2 (matching your code)
const interp = new CurveInterpolator(testPoints, { tension: 0.2 });

// Test lookup at the gap indices
console.log('\nInterpolated values at gap indices:');
const gapIndices = [3, 4];

gapIndices.forEach(i => {
    try {
        const result = interp.lookup(i);
        console.log(`Index ${i}:`);
        console.log(`  Full result: ${JSON.stringify(result)}`);
        if (result && result.length > 0) {
            console.log(`  Y-value: ${result[0][1]}`);
        }
    } catch (e) {
        console.log(`  Error: ${e.message}`);
    }
});

// Also test getIntersects (alternative method)
console.log('\nTrying getIntersects method:');
gapIndices.forEach(i => {
    try {
        const result = interp.getIntersects(i, 0, 1); // axis=0 (x-axis), max=1 (first intersection)
        console.log(`Index ${i}:`);
        console.log(`  Full result: ${JSON.stringify(result)}`);
        if (result && result.length > 0) {
            console.log(`  Y-value: ${result[0][1]}`);
        }
    } catch (e) {
        console.log(`  Error: ${e.message}`);
    }
});

// Test with your actual algorithm structure
console.log('\n\nFull algorithm test:');
console.log('====================');

const ibi_indexed = [[0, 520], [1, 505], [2, 515], [5, 510], [6, 500], [7, 495]];
const interpolation_indices = [[3, 4]];

console.log('Real IBIs:', JSON.stringify(ibi_indexed));
console.log('Indices to interpolate:', JSON.stringify(interpolation_indices));

const ibi_indexed_interpolated = new CurveInterpolator(ibi_indexed, { tension: 0.2 });

const interpolated_values_grouped = interpolation_indices.map(indexGroup => {
    return indexGroup.map(i => {
        const result = ibi_indexed_interpolated.lookup(i);
        return [i, result[0][1]];
    });
});

console.log('Interpolated values (raw):', JSON.stringify(interpolated_values_grouped));

// Scale them (matching your JS code)
const gap_duration = 515 - 505; // Original gap was from index 2 to 5
const interpolated_sum = interpolated_values_grouped[0].reduce((sum, v) => sum + v[1], 0);
const scale = gap_duration / interpolated_sum;

const scaled_values = interpolated_values_grouped[0].map(v => [v[0], Math.round(v[1] * scale)]);
console.log('Interpolated values (scaled):', JSON.stringify(scaled_values));