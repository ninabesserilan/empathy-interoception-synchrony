import { CurveInterpolator } from "curve-interpolator";

let input = "";
process.stdin.on("data", chunk => input += chunk);

process.stdin.on("end", () => {
  const {
    ibi_indexed,
    interpolation_groups,
    tension = 0.2
  } = JSON.parse(input);

  const interpolator = new CurveInterpolator(ibi_indexed, { tension });

  const values = interpolation_groups.map(group =>
    group.map(i => {
      return [i, interpolator.lookup(i)[0][1]];
    })
  );

  console.log(JSON.stringify(values));
});

