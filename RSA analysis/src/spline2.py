import math

def interpolate_curve(points, tension=0.0, alpha=0.0):
    """
    Given a list of [x, y] points, returns a function f(u) that computes
    the interpolated [x, y] at parameter u in [0, 1] along the curve.
    """
    n = len(points)
    if n == 0:
        raise ValueError("At least one point is required")
    if n == 1:
        # Only one point: always return it.
        def single_pt(u):
            return points[0].copy()
        return single_pt

    # Compute knot times (t-values) based on alpha parameter
    t = [0.0]
    for i in range(n - 1):
        dx = points[i+1][0] - points[i][0]
        dy = points[i+1][1] - points[i][1]
        dist = math.hypot(dx, dy)
        if alpha == 0.0:
            # Uniform spacing
            t.append(t[-1] + 1.0)
        else:
            # Centripetal/chordal spacing
            t.append(t[-1] + (dist ** alpha))
    total_time = t[-1]

    def get_point_at(u):
        """Interpolate the curve at parameter u in [0,1]."""
        # Clamp u to [0,1]
        u = max(0.0, min(1.0, u))
        # Map u to the global time parameter
        T = u * total_time

        # Find segment index i such that t[i] <= T <= t[i+1]
        # (Linear search; for efficiency, binary search can be used.)
        i = 0
        while i < n - 1 and T > t[i+1]:
            i += 1
        # Handle the extreme case where u == 1.0
        if i == n - 1:
            i = n - 2

        # Determine four indices for points (with extrapolation at ends)
        i0 = i - 1
        i1 = i
        i2 = i + 1
        i3 = i + 2

        # Extrapolate before first or after last if needed
        if i0 < 0:
            # Extrapolate virtual P0 from P1 and P2 direction
            P0 = [
                2*points[0][0] - points[1][0],
                2*points[0][1] - points[1][1]
            ]
        else:
            P0 = points[i0]
        P1 = points[i1]
        P2 = points[i2] if i2 < n else None
        P3 = points[i3] if i3 < n else None

        if P2 is None:
            # Extrapolate last point P2 from last two actual points
            P2 = [
                2*points[-1][0] - points[-2][0],
                2*points[-1][1] - points[-2][1]
            ]
        if P3 is None:
            # Extrapolate P3 (one beyond end) similarly
            if i1 >= n-2:
                P3 = [
                    2*points[-1][0] - points[-2][0],
                    2*points[-1][1] - points[-2][1]
                ]
            else:
                P3 = points[i1+3]  # or extrapolate again if needed

        # Local parameter within this segment [t[i], t[i+1]]
        t0, t1, t2, t3 = t[i0] if i0>=0 else 0.0, t[i1], t[i2], t[i3] if i3 < len(t) else (total_time + 1.0)
        # Because we manually set P0,P3 above, we recompute t0 and t3 consistently:
        if i0 < 0:
            t0 = t1 - (t2 - t1)
        if i3 >= len(t):
            t3 = t2 + (t2 - t1)

        # Compute local parameter s in [0,1] for segment [t1,t2]
        if (t2 - t1) != 0:
            s = (T - t1) / (t2 - t1)
        else:
            s = 0.0

        # Compute tangents (Cardinal spline formula with tension)
        # Tangent at P1 based on P2-P0, and at P2 based on P3-P1
        # Note: (1 - tension) factor scales the effect of curvature.
        dt1 = t2 - t0
        dt2 = t3 - t1
        if dt1 != 0:
            m1x = (P2[0] - P0[0]) / dt1
            m1y = (P2[1] - P0[1]) / dt1
        else:
            m1x = m1y = 0.0
        if dt2 != 0:
            m2x = (P3[0] - P1[0]) / dt2
            m2y = (P3[1] - P1[1]) / dt2
        else:
            m2x = m2y = 0.0
        m1x *= (1.0 - tension)
        m1y *= (1.0 - tension)
        m2x *= (1.0 - tension)
        m2y *= (1.0 - tension)

        # Hermite basis functions for parameter s
        s2 = s*s
        s3 = s2*s
        h00 =  2*s3 - 3*s2 + 1
        h10 =      s3 - 2*s2 + s
        h01 = -2*s3 + 3*s2
        h11 =      s3 -    s2

        # Interpolated point = h00*P1 + h10*(t2-t1)*m1 + h01*P2 + h11*(t2-t1)*m2
        segment_time = (t2 - t1)
        x = (h00 * P1[0] +
             h10 * segment_time * m1x +
             h01 * P2[0] +
             h11 * segment_time * m2x)
        y = (h00 * P1[1] +
             h10 * segment_time * m1y +
             h01 * P2[1] +
             h11 * segment_time * m2y)
        return [x, y]

    return get_point_at


def make_index_interpolator(points, tension=0.2, alpha=0.0):
    """
    Returns a function f(x_index) → interpolated y value,
    matching CurveInterpolator behavior.
    """
    points = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in points]
    x_min, x_max = xs[0], xs[-1]

    curve = interpolate_curve(points, tension=tension, alpha=alpha)

    def f(x):
        # clamp
        if x <= x_min:
            return points[0][1]
        if x >= x_max:
            return points[-1][1]

        # normalize index → u ∈ [0,1]
        u = (x - x_min) / (x_max - x_min)

        _, y = curve(u)
        return y

    return f
