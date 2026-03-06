"""
Tools for interacting with HalbachMRIDesigner system
"""

import json
import os
import subprocess
import tempfile
import sys
import numpy as np
from typing import Dict, Any, Optional
import shutil


def load_design_json(json_file_path: str = None) -> Dict[str, Any]:
    """
    Load a Halbach design from JSON file.
    
    Args:
        json_file_path: Path to the JSON file. If None, loads the default mri1.json
    
    Returns:
        Dictionary containing the design parameters
    """
    if json_file_path is None:
        json_file_path = '/Users/ivanetoku/Desktop/magnetAgent/HalbachMRIDesigner/examples/mri1.json'
    
    try:
        with open(json_file_path, 'r') as f:
            design = json.load(f)
        return {
            "status": "success",
            "design": design,
            "file_path": json_file_path,
            "message": f"Loaded design from {os.path.basename(json_file_path)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load JSON: {str(e)}"
        }


def update_design_json(
    design: Dict[str, Any],
    output_file: str = None,
    magnet_dimension: Optional[float] = None,
    magnet_br: Optional[float] = None,
    rings: Optional[list] = None
) -> Dict[str, Any]:
    """
    Update design parameters in a JSON structure and save to file.
    
    Args:
        design: The design dictionary to update
        output_file: Path to save updated JSON. If None, saves to outputs/current_design.json
        magnet_dimension: New magnet dimension (optional)
        magnet_br: New magnet BR value (optional)
        rings: New rings configuration (optional, list of dicts with id, radius, numMagnets)
    
    Returns:
        Dictionary with updated design and file path
    """
    try:
        # Update magnet properties if provided
        if magnet_dimension is not None:
            design["magnets"][0]["dimension"] = str(magnet_dimension)
        
        if magnet_br is not None:
            design["magnets"][0]["BR"] = str(magnet_br)
        
        # Update rings if provided
        if rings is not None:
            design["rings"] = rings
        
        # Save to file
        if output_file is None:
            output_dir = '/Users/ivanetoku/Desktop/magnetAgent/outputs'
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'current_design.json')
        
        with open(output_file, 'w') as f:
            json.dump(design, f, indent=2)
        
        return {
            "status": "success",
            "design": design,
            "file_path": output_file,
            "message": f"Design saved to {os.path.basename(output_file)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to update design: {str(e)}"
        }


def simulate_design_from_json(json_file_path: str) -> Dict[str, Any]:
    """
    Simulate a Halbach design from a JSON file and generate 3D B0 map.
    
    Args:
        json_file_path: Path to the JSON design file
    
    Returns:
        Dictionary with simulation results and 3D B0 map information
    """
    try:
        # Add HalbachMRIDesigner to Python path
        halbach_dir = '/Users/ivanetoku/Desktop/magnetAgent/HalbachMRIDesigner'
        if halbach_dir not in sys.path:
            sys.path.insert(0, halbach_dir)
        from HalbachCylinder import HalbachCylinder
        
        # Load the design
        halbachCylinder = HalbachCylinder()
        halbachCylinder.loadJSON(json_file_path)
        
        # Generate 3D B0 field map
        resolution = 0.005  # 5mm resolution
        dsv = 0.2  # 200mm diameter spherical volume
        simDimensions = (dsv, dsv, dsv)
        
        # Create 3D grid
        x = np.linspace(-simDimensions[0]/2, simDimensions[0]/2, 
                       int(simDimensions[0]/resolution)+1, dtype=np.float32)
        y = np.linspace(-simDimensions[1]/2, simDimensions[1]/2, 
                       int(simDimensions[1]/resolution)+1, dtype=np.float32)
        z = np.linspace(-simDimensions[2]/2, simDimensions[2]/2, 
                       int(simDimensions[2]/resolution)+1, dtype=np.float32)
        
        grid = np.meshgrid(x, y, z)
        
        # Create spherical mask
        mask = np.zeros(np.shape(grid[0]))
        mask[np.square(grid[0]) + np.square(grid[1]) + np.square(grid[2]) <= (dsv/2)**2] = 1
        
        # Extract evaluation points within sphere
        evalPoints = [g[mask==1] for g in grid]
        
        # Calculate B field at all points
        print(f"Calculating B field at {len(evalPoints[0])} points...")
        B0 = halbachCylinder.calculateB(evalPoints)
        
        # Calculate statistics
        max_b0 = np.amax(B0)
        B0z0 = B0[evalPoints[2]==0, :]
        B_abs = np.linalg.norm(B0z0[:, 0:1], axis=1)
        homogeneity = ((np.max(B_abs)-np.min(B_abs))/np.mean(B_abs))*1e6
        
        # Save 3D B0 map data
        output_dir = '/Users/ivanetoku/Desktop/magnetAgent/outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        design_name = os.path.splitext(os.path.basename(json_file_path))[0]
        b0_map_file = os.path.join(output_dir, f'b0_map_3d_{design_name}.npz')
        np.savez(b0_map_file,
                 B_field=B0,
                 eval_points_x=evalPoints[0],
                 eval_points_y=evalPoints[1],
                 eval_points_z=evalPoints[2],
                 grid_x=x,
                 grid_y=y,
                 grid_z=z,
                 mask=mask,
                 resolution=resolution,
                 dsv=dsv)
        
        print(f"3D B0 map saved to: {b0_map_file}")
        print(f"Max B0 amplitude is {max_b0} T")
        print(f"Homogeneity: {homogeneity} ppm")
        
        return {
            "status": "success",
            "max_field_strength": f"{max_b0} T",
            "homogeneity_ppm": f"{homogeneity} ppm",
            "design_file": json_file_path,
            "b0_map_file": b0_map_file,
            "grid_points": len(evalPoints[0]),
            "resolution_mm": resolution * 1000,
            "dsv_mm": dsv * 1000,
            "output": f"3D B0 map generated with {len(evalPoints[0])} points",
            "error": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to simulate design: {str(e)}"
        }


def generate_halbach_design(
    magnet_dimension: float,
    magnet_br: float,
    inner_radius: float,
    num_magnets: int,
    num_rings: int
) -> Dict[str, Any]:
    """
    Generate a Halbach array design with simplified parameters.
    
    Args:
        magnet_dimension: Size of each cube magnet in mm (e.g., 12)
        magnet_br: Remanence field strength in Tesla (e.g., 1.3)
        inner_radius: Starting inner radius in mm (e.g., 148)
        num_magnets: Number of magnets in first ring (e.g., 50)
        num_rings: Number of rings in the array (e.g., 19)
    
    Returns:
        Dictionary with design details including field strength and homogeneity
    """
    
    # Create a temporary JSON file with the design parameters
    design_params = {
        "_comment": "Generated by Halbach Magnet Design Agent",
        "magnets": [
            {
                "dimension": str(magnet_dimension),
                "shape": "cube",
                "BR": str(magnet_br),
                "mur": "1"
            }
        ],
        "defaultMagnetType": 0,
        "rings": [],
        "slices": [],
        "mirrorSlices": True,
        "numConnectionRods": 12,
        "connectionRodsDiameter": 5,
        "connectionRodsArcRadius": 165,
        "standHeight": 0,
        "standWidth": 0
    }
    
    # Generate rings with incremental radius and magnet count
    radius_increment = 3
    for i in range(num_rings):
        design_params["rings"].append({
            "id": i,
            "radius": int(inner_radius + i * radius_increment),
            "numMagnets": int(num_magnets + i)
        })
    
    # Generate slices (simplified - single slice at center)
    max_radius = inner_radius + (num_rings - 1) * radius_increment + 50
    design_params["slices"].append({
        "position": 0,
        "innerRadius": int(inner_radius - 20),
        "outerRadius": int(max_radius),
        "rings": [{"id": i} for i in range(num_rings)]
    })
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(design_params, f, indent=2)
        temp_file = f.name
    
    try:
        # Run HalbachMRIDesigner to generate 3D B0 map
        # Use absolute path to HalbachMRIDesigner
        halbach_dir = '/Users/ivanetoku/Desktop/magnetAgent/HalbachMRIDesigner'
        halbach_script = os.path.join(halbach_dir, 'HalbachMRIDesigner.py')
        
        # Add HalbachMRIDesigner to Python path and import it
        sys.path.insert(0, halbach_dir)
        from HalbachCylinder import HalbachCylinder
        
        # Load the design
        halbachCylinder = HalbachCylinder()
        halbachCylinder.loadJSON(temp_file)
        
        # Generate 3D B0 field map
        resolution = 0.005  # 5mm resolution
        dsv = 0.2  # 200mm diameter spherical volume
        simDimensions = (dsv, dsv, dsv)
        
        # Create 3D grid
        x = np.linspace(-simDimensions[0]/2, simDimensions[0]/2, 
                       int(simDimensions[0]/resolution)+1, dtype=np.float32)
        y = np.linspace(-simDimensions[1]/2, simDimensions[1]/2, 
                       int(simDimensions[1]/resolution)+1, dtype=np.float32)
        z = np.linspace(-simDimensions[2]/2, simDimensions[2]/2, 
                       int(simDimensions[2]/resolution)+1, dtype=np.float32)
        
        grid = np.meshgrid(x, y, z)
        
        # Create spherical mask
        mask = np.zeros(np.shape(grid[0]))
        mask[np.square(grid[0]) + np.square(grid[1]) + np.square(grid[2]) <= (dsv/2)**2] = 1
        
        # Extract evaluation points within sphere
        evalPoints = [g[mask==1] for g in grid]
        
        # Calculate B field at all points
        print(f"Calculating B field at {len(evalPoints[0])} points...")
        B0 = halbachCylinder.calculateB(evalPoints)
        
        # Calculate statistics
        max_b0 = np.amax(B0)
        B0z0 = B0[evalPoints[2]==0, :]
        B_abs = np.linalg.norm(B0z0[:, 0:1], axis=1)
        homogeneity = ((np.max(B_abs)-np.min(B_abs))/np.mean(B_abs))*1e6
        
        # Save 3D B0 map data
        output_dir = '/Users/ivanetoku/Desktop/magnetAgent/outputs'
        os.makedirs(output_dir, exist_ok=True)
        
        b0_map_file = os.path.join(output_dir, 'b0_map_3d.npz')
        np.savez(b0_map_file,
                 B_field=B0,
                 eval_points_x=evalPoints[0],
                 eval_points_y=evalPoints[1],
                 eval_points_z=evalPoints[2],
                 grid_x=x,
                 grid_y=y,
                 grid_z=z,
                 mask=mask,
                 resolution=resolution,
                 dsv=dsv)
        
        print(f"3D B0 map saved to: {b0_map_file}")
        print(f"Max B0 amplitude is {max_b0} T")
        print(f"Homogeneity: {homogeneity} ppm")
        
        return {
            "status": "success",
            "max_field_strength": f"{max_b0} T",
            "homogeneity_ppm": f"{homogeneity} ppm",
            "design_file": temp_file,
            "b0_map_file": b0_map_file,
            "grid_points": len(evalPoints[0]),
            "resolution_mm": resolution * 1000,
            "dsv_mm": dsv * 1000,
            "output": f"3D B0 map generated with {len(evalPoints[0])} points",
            "error": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to generate 3D B0 map: {str(e)}"
        }
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def validate_design_parameters(
    magnet_dimension: float,
    magnet_br: float,
    inner_radius: float,
    num_magnets: int,
    num_rings: int
) -> Dict[str, Any]:
    """
    Validate design parameters for physical feasibility.
    
    Returns:
        Dictionary with validation results
    """
    issues = []
    
    # Check magnet dimension
    if magnet_dimension < 5 or magnet_dimension > 50:
        issues.append("Magnet dimension should be between 5mm and 50mm for practical manufacturing")
    
    # Check BR (typical range for NdFeB magnets)
    if magnet_br < 0.5 or magnet_br > 1.5:
        issues.append("Remanence field (BR) should be between 0.5T and 1.5T for NdFeB magnets")
    
    # Check inner radius
    if inner_radius < 50:
        issues.append("Inner radius should be at least 50mm for practical designs")
    
    # Check num magnets
    if num_magnets < 20 or num_magnets > 100:
        issues.append("Number of magnets per ring should be between 20 and 100")
    
    # Check num rings
    if num_rings < 5 or num_rings > 30:
        issues.append("Number of rings should be between 5 and 30")
    
    # Check magnet spacing
    circumference = 2 * 3.14159 * inner_radius
    magnet_spacing = circumference / num_magnets
    if magnet_spacing < magnet_dimension * 0.8:
        issues.append(f"Magnets may overlap: spacing ({magnet_spacing:.1f}mm) < magnet dimension ({magnet_dimension}mm)")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": [] if len(issues) == 0 else ["Please adjust parameters to address issues"]
    }


def calculate_bom(
    magnet_dimension: float,
    magnet_br: float,
    num_magnets: int,
    num_rings: int
) -> Dict[str, Any]:
    """
    Calculate bill of materials for the Halbach array.
    
    Returns:
        Dictionary with BOM information
    """
    total_magnets = 0
    for i in range(num_rings):
        total_magnets += (num_magnets + i)
    
    # Calculate volume per magnet (cube)
    magnet_volume_cm3 = (magnet_dimension / 10) ** 3
    total_volume_cm3 = total_magnets * magnet_volume_cm3
    
    # Estimate weight (NdFeB density ~7.5 g/cm³)
    total_weight_kg = total_volume_cm3 * 7.5 / 1000
    
    # Estimate cost (rough estimate: $50-100 per kg for NdFeB)
    estimated_cost_usd = total_weight_kg * 75
    
    return {
        "total_magnets": total_magnets,
        "magnet_type": f"NdFeB N42 (BR={magnet_br}T)",
        "magnet_dimensions": f"{magnet_dimension}mm cube",
        "total_volume_cm3": round(total_volume_cm3, 2),
        "total_weight_kg": round(total_weight_kg, 2),
        "estimated_cost_usd": round(estimated_cost_usd, 2),
        "notes": [
            "Cost estimate based on average NdFeB pricing",
            "Add 10-20% for structural components and mounting",
            "Prices vary significantly by supplier and quantity"
        ]
    }


def visualize_b0_map_3d(b0_map_file: str = None) -> Dict[str, Any]:
    """
    Create visualization plots from a saved 3D B0 map.
    
    Args:
        b0_map_file: Path to the .npz file containing B0 map data.
                    If None, uses the default output location.
    
    Returns:
        Dictionary with visualization status and file paths
    """
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        # Load B0 map data
        if b0_map_file is None:
            b0_map_file = '/Users/ivanetoku/Desktop/magnetAgent/outputs/b0_map_3d.npz'
        
        if not os.path.exists(b0_map_file):
            return {
                "status": "error",
                "error": f"B0 map file not found: {b0_map_file}"
            }
        
        data = np.load(b0_map_file)
        B_field = data['B_field']
        eval_x = data['eval_points_x']
        eval_y = data['eval_points_y']
        eval_z = data['eval_points_z']
        
        # Calculate field magnitude
        B_magnitude = np.linalg.norm(B_field, axis=1)
        
        output_dir = os.path.dirname(b0_map_file)
        plot_files = []
        
        # 1. Central slice (z=0) contour plot
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        z0_mask = eval_z == 0
        if np.any(z0_mask):
            x_z0 = eval_x[z0_mask]
            y_z0 = eval_y[z0_mask]
            B_z0 = B_magnitude[z0_mask]
            
            contour = ax1.tricontourf(x_z0*1000, y_z0*1000, B_z0, levels=20, cmap='jet')
            plt.colorbar(contour, ax=ax1, label='B0 Field (T)')
            ax1.set_xlabel('X (mm)')
            ax1.set_ylabel('Y (mm)')
            ax1.set_title('B0 Field Map - Central Slice (z=0)')
            ax1.set_aspect('equal')
            
            slice_file = os.path.join(output_dir, 'b0_map_slice_z0.png')
            plt.savefig(slice_file, dpi=150, bbox_inches='tight')
            plot_files.append(slice_file)
            plt.close(fig1)
        
        # 2. 3D scatter plot (sampled points for visibility)
        fig2 = plt.figure(figsize=(12, 10))
        ax2 = fig2.add_subplot(111, projection='3d')
        
        # Sample every nth point for visualization
        sample_step = max(1, len(eval_x) // 5000)
        sample_indices = np.arange(0, len(eval_x), sample_step)
        
        # Swap X and Y coordinates
        scatter = ax2.scatter(eval_y[sample_indices]*1000,  # Y on X-axis
                            eval_x[sample_indices]*1000,  # X on Y-axis
                            eval_z[sample_indices]*1000,
                            c=B_magnitude[sample_indices],
                            cmap='jet',
                            s=1,
                            alpha=0.6)
        
        # Remove labels but keep axis lines
        ax2.set_xlabel('')
        ax2.set_ylabel('')
        ax2.set_zlabel('')
        ax2.set_title('')
        ax2.set_xticklabels([])
        ax2.set_yticklabels([])
        ax2.set_zticklabels([])
        
        scatter_file = os.path.join(output_dir, 'b0_map_3d_scatter.png')
        plt.savefig(scatter_file, dpi=150, bbox_inches='tight')
        plot_files.append(scatter_file)
        plt.close(fig2)
        
        # 2a. 3D Continuous surface plot (dense point cloud rendered as surface)
        try:
            fig2a = plt.figure(figsize=(14, 12))
            ax2a = fig2a.add_subplot(111, projection='3d')
            
            # Use all points (or densely sample) for a continuous look
            sample_step = max(1, len(eval_x) // 10000)  # Denser sampling
            sample_indices = np.arange(0, len(eval_x), sample_step)
            
            # Create a continuous-looking plot using very small points with high density
            # NOTE: X and Y are interchanged for better visualization
            scatter = ax2a.scatter(eval_y[sample_indices]*1000,  # Y on X-axis
                                  eval_x[sample_indices]*1000,  # X on Y-axis
                                  eval_z[sample_indices]*1000,
                                  c=B_magnitude[sample_indices],
                                  cmap='jet',
                                  s=20,  # Larger points
                                  alpha=0.8,
                                  marker='o',
                                  edgecolors='none')
            
            # Remove labels but keep axis lines
            ax2a.set_xlabel('')
            ax2a.set_ylabel('')
            ax2a.set_zlabel('')
            ax2a.set_title('')
            ax2a.set_xticklabels([])
            ax2a.set_yticklabels([])
            ax2a.set_zticklabels([])
            
            # Match the same view as scatter plot
            ax2a.view_init(elev=20, azim=45)
            
            # Set background color for better contrast
            ax2a.xaxis.pane.fill = False
            ax2a.yaxis.pane.fill = False
            ax2a.zaxis.pane.fill = False
            
            surface_file = os.path.join(output_dir, 'b0_map_3d_continuous.png')
            plt.savefig(surface_file, dpi=200, bbox_inches='tight', facecolor='white')
            plot_files.append(surface_file)
            plt.close(fig2a)
            
        except Exception as e:
            print(f"Note: Could not create continuous surface plot: {e}")
        
        # 2b. Continuous 3D volume visualization with slice planes
        fig2b = plt.figure(figsize=(14, 12))
        ax2b = fig2b.add_subplot(111, projection='3d')
        
        # Load full grid data
        grid_x = data['grid_x']
        grid_y = data['grid_y']
        grid_z = data['grid_z']
        mask = data['mask']
        
        # Reconstruct 3D field magnitude grid
        full_shape = mask.shape
        B_mag_grid = np.zeros(full_shape)
        
        # Map evaluation points back to grid
        for i, (x, y, z, b) in enumerate(zip(eval_x, eval_y, eval_z, B_magnitude)):
            # Find indices in grid
            ix = np.argmin(np.abs(grid_x - x))
            iy = np.argmin(np.abs(grid_y - y))
            iz = np.argmin(np.abs(grid_z - z))
            B_mag_grid[iy, ix, iz] = b
        
        # Create multiple slice planes for continuous visualization
        X_grid, Y_grid, Z_grid = np.meshgrid(grid_x, grid_y, grid_z)
        
        # Plot slices at different positions
        slice_positions_z = [0, grid_z[len(grid_z)//4], grid_z[3*len(grid_z)//4]]
        slice_positions_x = [0, grid_x[len(grid_x)//4], grid_x[3*len(grid_x)//4]]
        slice_positions_y = [0]
        
        # Z-plane slices (horizontal)
        for z_pos in slice_positions_z:
            iz = np.argmin(np.abs(grid_z - z_pos))
            if np.any(mask[:, :, iz]):
                # Get slice data
                slice_B = B_mag_grid[:, :, iz]
                slice_B_masked = np.ma.masked_where(mask[:, :, iz] == 0, slice_B)
                
                # Create meshgrid for this slice
                X_slice, Y_slice = np.meshgrid(grid_x, grid_y)
                Z_slice = np.ones_like(X_slice) * z_pos
                
                # Plot continuous surface
                surf = ax2b.plot_surface(X_slice*1000, Y_slice*1000, Z_slice*1000,
                                        facecolors=plt.cm.jet((slice_B_masked - slice_B_masked.min()) / 
                                                             (slice_B_masked.max() - slice_B_masked.min() + 1e-10)),
                                        alpha=0.6, shade=False, linewidth=0, antialiased=True)
        
        # Y-plane slices (vertical)
        for y_pos in slice_positions_y:
            iy = np.argmin(np.abs(grid_y - y_pos))
            if np.any(mask[iy, :, :]):
                slice_B = B_mag_grid[iy, :, :]
                slice_B_masked = np.ma.masked_where(mask[iy, :, :] == 0, slice_B)
                
                X_slice, Z_slice = np.meshgrid(grid_x, grid_z)
                Y_slice = np.ones_like(X_slice) * y_pos
                
                surf = ax2b.plot_surface(X_slice*1000, Y_slice*1000, Z_slice*1000,
                                        facecolors=plt.cm.jet((slice_B_masked.T - slice_B_masked.min()) / 
                                                             (slice_B_masked.max() - slice_B_masked.min() + 1e-10)),
                                        alpha=0.6, shade=False, linewidth=0, antialiased=True)
        
        # Add colorbar
        m = plt.cm.ScalarMappable(cmap='jet')
        m.set_array([B_magnitude.min(), B_magnitude.max()])
        m.set_clim(B_magnitude.min(), B_magnitude.max())
        plt.colorbar(m, ax=ax2b, label='B0 Field (T)', shrink=0.5, pad=0.1)
        
        ax2b.set_xlabel('X (mm)')
        ax2b.set_ylabel('Y (mm)')
        ax2b.set_zlabel('Z (mm)')
        ax2b.set_title('3D B0 Field - Continuous Volume Slices')
        
        # Set equal aspect ratio
        max_range = max([grid_x.max()-grid_x.min(), grid_y.max()-grid_y.min(), grid_z.max()-grid_z.min()]) * 1000 / 2
        mid_x = (grid_x.max()+grid_x.min()) * 1000 / 2
        mid_y = (grid_y.max()+grid_y.min()) * 1000 / 2
        mid_z = (grid_z.max()+grid_z.min()) * 1000 / 2
        ax2b.set_xlim(mid_x - max_range, mid_x + max_range)
        ax2b.set_ylim(mid_y - max_range, mid_y + max_range)
        ax2b.set_zlim(mid_z - max_range, mid_z + max_range)
        
        volume_file = os.path.join(output_dir, 'b0_map_3d_volume_slices.png')
        plt.savefig(volume_file, dpi=150, bbox_inches='tight')
        plot_files.append(volume_file)
        plt.close(fig2b)
        
        # 3. Field magnitude histogram
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        ax3.hist(B_magnitude, bins=50, edgecolor='black', alpha=0.7)
        ax3.set_xlabel('B0 Field Magnitude (T)')
        ax3.set_ylabel('Number of Points')
        ax3.set_title('B0 Field Distribution Histogram')
        ax3.axvline(np.mean(B_magnitude), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(B_magnitude):.4f} T')
        ax3.legend()
        
        hist_file = os.path.join(output_dir, 'b0_field_histogram.png')
        plt.savefig(hist_file, dpi=150, bbox_inches='tight')
        plot_files.append(hist_file)
        plt.close(fig3)
        
        # Statistics
        stats = {
            "mean_field": float(np.mean(B_magnitude)),
            "max_field": float(np.max(B_magnitude)),
            "min_field": float(np.min(B_magnitude)),
            "std_field": float(np.std(B_magnitude)),
            "homogeneity_ppm": float(((np.max(B_magnitude)-np.min(B_magnitude))/np.mean(B_magnitude))*1e6)
        }
        
        return {
            "status": "success",
            "plot_files": plot_files,
            "statistics": stats,
            "message": f"Generated {len(plot_files)} visualization plots"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to visualize B0 map: {str(e)}"
        }

